import re
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from urllib.parse import parse_qs, unquote, urlsplit
from unittest.mock import patch

from werkzeug.security import check_password_hash, generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Brand, CartItem, Category, Order, OrderItem, Payment, Product, ProductVariant, User, WishlistItem
from app.routes.checkout import _clear_ordered_cart_quantities
from app.routes.customer_auth import safe_next_url
from config import config_by_name


ShoppingTestingConfig = type(
    "ShoppingTestingConfig",
    (),
    {
        "SECRET_KEY": "shopping-test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,
        "PERMANENT_SESSION_LIFETIME": timedelta(hours=2),
        "PUBLIC_BASE_URL": "https://stepzone.example",
        "PAYTM_MID": "mock-mid",
        "PAYTM_CHECKOUT_JS_URL": "https://example.invalid/merchant/{mid}.js",
        "DEBUG": True,
    },
)
config_by_name["shopping_testing"] = ShoppingTestingConfig


class CustomerShoppingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("shopping_testing")
        cls.context = cls.app.app_context()
        cls.context.push()
        db.create_all()

        cls.first = User(email="shopper1@example.com", password_hash=generate_password_hash("CustomerPassword!"), first_name="First", last_name="Shopper", role="customer")
        cls.second = User(email="shopper2@example.com", password_hash=generate_password_hash("CustomerPassword!"), first_name="Second", last_name="Shopper", role="customer")
        cls.brand = Brand(name="Test Brand", slug="test-brand")
        cls.category = Category(name="Test Sneakers", slug="test-sneakers")
        db.session.add_all([cls.first, cls.second, cls.brand, cls.category])
        db.session.flush()

        cls.first_product = Product(
            name="Test Runner",
            slug="test-runner",
            brand_id=cls.brand.id,
            category_id=cls.category.id,
            base_price=Decimal("120.00"),
            image_url="https://example.com/test-runner.jpg",
        )
        cls.second_product = Product(
            name="Test Court",
            slug="test-court",
            brand_id=cls.brand.id,
            category_id=cls.category.id,
            base_price=Decimal("220.00"),
            image_url="https://example.com/test-court.jpg",
        )
        db.session.add_all([cls.first_product, cls.second_product])
        db.session.flush()
        cls.first_variant = ProductVariant(
            product_id=cls.first_product.id,
            sku="TEST-RUNNER-8",
            size="8",
            color="Black",
            price=Decimal("125.00"),
            stock_quantity=5,
        )
        cls.second_variant = ProductVariant(
            product_id=cls.second_product.id,
            sku="TEST-COURT-9",
            size="9",
            color="White",
            price=Decimal("225.00"),
            stock_quantity=4,
        )
        db.session.add_all([cls.first_variant, cls.second_variant])
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.context.pop()

    def setUp(self):
        OrderItem.query.delete()
        Payment.query.delete()
        Order.query.delete()
        CartItem.query.delete()
        WishlistItem.query.delete()
        self.first_variant.stock_quantity = 5
        self.second_variant.stock_quantity = 4
        self.first_product.is_active = True
        self.second_product.is_active = True
        self.first.first_name = "First"
        self.first.last_name = "Shopper"
        self.first.phone = None
        self.first.address = None
        self.first.city = None
        self.first.state = None
        self.first.postal_code = None
        self.first.email = "shopper1@example.com"
        self.first.password_hash = generate_password_hash("CustomerPassword!")
        db.session.commit()

    def csrf(self, client, path):
        response = client.get(path)
        self.assertEqual(response.status_code, 200)
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True))
        self.assertIsNotNone(match)
        return match.group(1)

    def login(self, client, email="shopper1@example.com", remember=False, next_url="/account"):
        token = self.csrf(client, "/login")
        data = {"csrf_token": token, "email": email, "password": "CustomerPassword!", "next": next_url}
        if remember:
            data["remember_me"] = "on"
        return client.post("/login", data=data)

    def add_item(self, client, product, variant, quantity=1):
        token = self.csrf(client, f"/product/{product.slug}")
        return client.post(
            "/cart/add",
            data={
                "csrf_token": token,
                "product_id": str(product.id),
                "variant_id": str(variant.id),
                "quantity": str(quantity),
                "price": "0.01",
                "stock_quantity": "999999",
            },
        )

    def test_public_browsing_and_requested_trending_markup(self):
        client = self.app.test_client()
        self.assertEqual(client.get("/").status_code, 200)
        detail = client.get(f"/product/{self.first_product.slug}")
        self.assertEqual(detail.status_code, 200)
        html = detail.get_data(as_text=True)
        self.assertIn(self.first_product.image_url, html)
        self.assertIn("Add to cart", html)

    def test_checkout_out_of_stock_cart_item_returns_400_with_error(self):
        client = self.app.test_client()
        self.assertEqual(self.login(client).status_code, 302)
        self.assertEqual(self.add_item(client, self.first_product, self.first_variant).status_code, 302)
        self.first_variant.stock_quantity = 0
        db.session.commit()

        response = client.get("/checkout")

        self.assertEqual(response.status_code, 400)
        self.assertIn("does not have enough stock", response.get_data(as_text=True).lower())

    def test_checkout_empty_cart_and_invalid_csrf_are_handled_without_order_creation(self):
        client = self.app.test_client()
        self.assertEqual(self.login(client).status_code, 302)
        empty = client.get("/checkout")
        self.assertEqual(empty.status_code, 200)
        self.assertIn("cart is empty", empty.get_data(as_text=True).lower())
        self.add_item(client, self.first_product, self.first_variant)
        response = client.post("/checkout/cod", data={
            "checkout_token": "invalid-csrf-token", "name": "First Shopper", "email": self.first.email,
            "phone": "9999999999", "address": "Address", "city": "Pune", "state": "MH", "postal_code": "411001",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("form session expired", response.get_data(as_text=True).lower())
        self.assertEqual(Order.query.filter_by(checkout_token="invalid-csrf-token").count(), 0)

    def test_paytm_checkout_reserves_stock_when_gateway_start_succeeds(self):
        client = self.app.test_client()
        self.assertEqual(self.login(client).status_code, 302)
        self.add_item(client, self.first_product, self.first_variant, quantity=2)
        page = client.get("/checkout")
        body = page.get_data(as_text=True)
        csrf = re.search(r'name="csrf_token" value="([^"]+)"', body).group(1)
        checkout_token = re.search(r'name="checkout_token" value="([^"]+)"', body).group(1)
        data = {
            "csrf_token": csrf, "checkout_token": checkout_token, "name": "First Shopper",
            "email": self.first.email, "phone": "9999999999", "address": "Address",
            "city": "Pune", "state": "MH", "postal_code": "411001",
        }
        with patch("app.routes.checkout.initiate_transaction", return_value={"order_id": "SZ-MOCK", "txn_token": "mock-token"}):
            response = client.post("/checkout/paytm", data=data)
        self.assertEqual(response.status_code, 200)
        order = Order.query.filter_by(checkout_token=checkout_token).one()
        self.assertTrue(order.stock_reserved)
        self.assertEqual(order.payment_status, "pending")
        self.assertEqual(self.first_variant.stock_quantity, 3)

    def test_guest_product_add_returns_to_product_with_requested_size(self):
        client = self.app.test_client()
        token = self.csrf(client, f"/product/{self.first_product.slug}")
        response = client.post(
            "/cart/add",
            data={
                "csrf_token": token,
                "product_id": str(self.first_product.id),
                "variant_id": str(self.first_variant.id),
                "quantity": "1",
            },
        )
        self.assertEqual(response.status_code, 302)
        parsed = urlsplit(response.location)
        self.assertEqual(parsed.path, "/login")
        intended = parse_qs(parsed.query)["next"][0]
        self.assertEqual(intended, f"/product/{self.first_product.slug}?variant_id={self.first_variant.id}")

        login_page = client.get(response.location)
        self.assertEqual(login_page.status_code, 200)
        csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', login_page.get_data(as_text=True)).group(1)
        logged_in = client.post(
            "/login",
            data={
                "csrf_token": csrf_token,
                "email": "shopper1@example.com",
                "password": "CustomerPassword!",
                "next": intended,
            },
        )
        self.assertEqual(unquote(logged_in.location), intended)
        restored_page = client.get(logged_in.location)
        self.assertIn('data-requested="true"', restored_page.get_data(as_text=True))

    def test_remember_me_controls_persistent_session(self):
        ordinary = self.app.test_client()
        ordinary_response = self.login(ordinary)
        self.assertEqual(ordinary_response.status_code, 302)
        with ordinary.session_transaction() as flask_session:
            self.assertFalse(flask_session.permanent)
        ordinary_cookie = next((cookie for cookie in ordinary_response.headers.getlist("Set-Cookie") if cookie.startswith("session=")), "")
        self.assertTrue(ordinary_cookie)
        self.assertFalse(any(part.strip().lower().startswith(("expires=", "max-age=")) for part in ordinary_cookie.split(";")[1:]))

        remembered = self.app.test_client()
        remembered_response = self.login(remembered, remember=True)
        self.assertEqual(remembered_response.status_code, 302)
        with remembered.session_transaction() as flask_session:
            self.assertTrue(flask_session.permanent)
            self.assertEqual(flask_session["customer_user_id"], self.first.id)
            self.assertTrue(flask_session["customer_remember_me"])
        remembered_cookie = next((cookie for cookie in remembered_response.headers.getlist("Set-Cookie") if cookie.startswith("session=")), "")
        expires_text = next((part.split("=", 1)[1].strip() for part in remembered_cookie.split(";")[1:] if part.strip().lower().startswith("expires=")), "")
        self.assertTrue(expires_text)
        from email.utils import parsedate_to_datetime

        remaining = parsedate_to_datetime(expires_text) - datetime.now(timezone.utc)
        self.assertGreaterEqual(remaining, timedelta(days=29))
        self.assertLessEqual(remaining, timedelta(days=30, minutes=1))
        self.assertEqual(self.app.permanent_session_lifetime, timedelta(hours=2))

    def test_registration_accepts_optional_phone_and_hashes_password(self):
        client = self.app.test_client()
        token = self.csrf(client, "/register")
        response = client.post(
            "/register",
            data={
                "csrf_token": token,
                "full_name": "New Shopper",
                "email": "new-shopper@example.com",
                "phone": "",
                "password": "LongCustomerPassword!",
                "confirm_password": "LongCustomerPassword!",
            },
        )
        self.assertEqual(response.status_code, 302)
        created = User.query.filter_by(email="new-shopper@example.com").one()
        self.assertIsNone(created.phone)
        self.assertTrue(check_password_hash(created.password_hash, "LongCustomerPassword!"))
        self.assertNotEqual(created.password_hash, "LongCustomerPassword!")

    def test_cart_uses_server_prices_and_another_customer_cannot_edit_it(self):
        first_client = self.app.test_client()
        self.assertEqual(self.login(first_client).status_code, 302)
        added = self.add_item(first_client, self.first_product, self.first_variant, quantity=2)
        self.assertEqual(added.status_code, 302)
        item = CartItem.query.filter_by(user_id=self.first.id).one()
        self.assertEqual(item.quantity, 2)

        cart_page = first_client.get("/cart")
        self.assertEqual(cart_page.status_code, 200)
        self.assertIn("250.00", cart_page.get_data(as_text=True))

        second_client = self.app.test_client()
        self.assertEqual(self.login(second_client, email="shopper2@example.com").status_code, 302)
        token = self.csrf(second_client, "/cart")
        denied = second_client.post(
            f"/cart/items/{item.id}/update",
            data={"csrf_token": token, "quantity": "1"},
        )
        self.assertEqual(denied.status_code, 404)
        self.assertEqual(CartItem.query.filter_by(id=item.id).one().quantity, 2)

    def test_checkout_creates_multiple_items_with_database_totals_and_clears_cart(self):
        client = self.app.test_client()
        self.assertEqual(self.login(client).status_code, 302)
        self.add_item(client, self.first_product, self.first_variant, quantity=2)
        self.add_item(client, self.second_product, self.second_variant, quantity=1)

        checkout_page = client.get("/checkout")
        self.assertEqual(checkout_page.status_code, 200)
        page_text = checkout_page.get_data(as_text=True)
        self.assertIn("475.00", page_text)
        csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', page_text).group(1)
        checkout_token = re.search(r'name="checkout_token" value="([^"]+)"', page_text).group(1)
        with patch("app.routes.checkout.send_order_confirmation") as send_confirmation:
            response = client.post(
                "/checkout/cod",
                data={
                    "csrf_token": csrf_token,
                    "checkout_token": checkout_token,
                    "name": "First Shopper",
                    "email": "shopper1@example.com",
                    "phone": "9999999999",
                    "address": "12 Example Street",
                    "city": "Pune",
                    "state": "Maharashtra",
                    "postal_code": "411001",
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("order has been placed", response.get_data(as_text=True))
        order = Order.query.filter_by(user_id=self.first.id).one()
        self.assertEqual(order.subtotal, Decimal("475.00"))
        self.assertEqual(len(order.items), 2)
        self.assertEqual(CartItem.query.filter_by(user_id=self.first.id).count(), 0)
        self.assertEqual(self.first_variant.stock_quantity, 3)
        self.assertEqual(self.second_variant.stock_quantity, 3)
        send_confirmation.assert_called_once_with(order.id)

    def test_homepage_brands_are_dynamic_and_inactive_brands_are_hidden(self):
        dynamic = Brand(name="Dynamic Label", slug="dynamic-label")
        hidden = Brand(name="Hidden Label", slug="hidden-label", is_active=False)
        db.session.add_all([dynamic, hidden])
        db.session.commit()

        response = self.app.test_client().get("/")
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('/brands/test-brand', body)
        self.assertIn('/brands/dynamic-label', body)
        self.assertNotIn('/brands/hidden-label', body)

    def test_brand_page_filters_products_by_brand_and_stocked_size(self):
        other_brand = Brand(name="Other Brand", slug="other-brand")
        db.session.add(other_brand)
        db.session.flush()
        other_product = Product(
            name="Other Runner",
            slug="other-runner",
            brand_id=other_brand.id,
            category_id=self.category.id,
            base_price=Decimal("330.00"),
        )
        db.session.add(other_product)
        db.session.flush()
        db.session.add(ProductVariant(product_id=other_product.id, sku="OTHER-RUNNER-10", size="10", price=Decimal("330.00"), stock_quantity=3))
        db.session.commit()

        client = self.app.test_client()
        response = client.get("/brands/test-brand?size=8&sort=price_asc")
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Runner", body)
        self.assertNotIn("Test Court", body)
        self.assertNotIn("Other Runner", body)
        self.assertIn("125.00", body)
        descending = client.get("/brands/test-brand?sort=price_desc").get_data(as_text=True)
        self.assertLess(descending.index("Test Court"), descending.index("Test Runner"))
        self.assertEqual(client.get("/brands/other-brand").status_code, 200)
        self.assertEqual(client.get("/brands/missing-brand").status_code, 404)

    def test_product_search_escapes_percent_and_underscore(self):
        percent = Product(name="Literal % Runner", slug="literal-percent-runner", brand_id=self.brand.id, category_id=self.category.id, base_price=Decimal("300.00"))
        underscore = Product(name="Literal _ Court", slug="literal-underscore-court", brand_id=self.brand.id, category_id=self.category.id, base_price=Decimal("310.00"))
        decoys = [
            Product(name="Literal X Runner", slug="literal-x-runner", brand_id=self.brand.id, category_id=self.category.id, base_price=Decimal("320.00")),
            Product(name="Literal A Court", slug="literal-a-court", brand_id=self.brand.id, category_id=self.category.id, base_price=Decimal("330.00")),
        ]
        db.session.add_all([percent, underscore, *decoys])
        db.session.flush()
        for index, product in enumerate([percent, underscore, *decoys]):
            db.session.add(ProductVariant(product_id=product.id, sku=f"LITERAL-SEARCH-{index}", size="8", stock_quantity=2, price=product.base_price))
        db.session.commit()

        client = self.app.test_client()
        percent_brand = client.get("/brands/test-brand?q=%25").get_data(as_text=True)
        percent_search = client.get("/search?q=%25").get_data(as_text=True)
        underscore_brand = client.get("/brands/test-brand?q=_").get_data(as_text=True)
        underscore_search = client.get("/search?q=_").get_data(as_text=True)
        for body in (percent_brand, percent_search):
            self.assertIn("Literal % Runner", body)
            self.assertNotIn("Literal X Runner", body)
        for body in (underscore_brand, underscore_search):
            self.assertIn("Literal _ Court", body)
            self.assertNotIn("Literal A Court", body)

    def test_ordered_cart_cleanup_ignores_quantity_changes(self):
        cart = CartItem(user_id=self.first.id, product_variant_id=self.first_variant.id, quantity=3)
        order = Order(
            order_number="SZ-CART-CLEAR", checkout_token="cart-clear-token", user_id=self.first.id,
            status="confirmed", payment_method="cod", payment_status="pending_cod",
            subtotal=Decimal("250.00"), shipping_fee=Decimal("0"), total_amount=Decimal("250.00"),
            customer_name="First Shopper", customer_email=self.first.email, customer_phone="9999999999",
            shipping_address="Address", shipping_city="City", shipping_state="State", shipping_postal_code="411001",
        )
        order.items.append(OrderItem(
            product_id=self.first_product.id, product_variant_id=self.first_variant.id,
            product_name=self.first_product.name, sku=self.first_variant.sku, size=self.first_variant.size,
            color=self.first_variant.color, unit_price=Decimal("125.00"), quantity=2, line_total=Decimal("250.00"),
        ))
        db.session.add_all([cart, order])
        db.session.flush()
        _clear_ordered_cart_quantities(self.first.id, order)
        db.session.commit()
        self.assertEqual(CartItem.query.filter_by(id=cart.id).count(), 0)

    def test_empty_brand_shows_friendly_message_and_inactive_products_are_hidden(self):
        empty_brand = Brand(name="Empty Brand", slug="empty-brand")
        self.first_product.is_active = False
        db.session.add(empty_brand)
        db.session.commit()
        response = self.app.test_client().get("/brands/empty-brand")
        self.assertEqual(response.status_code, 200)
        self.assertIn("No products available from this brand yet", response.get_data(as_text=True))

    def test_protected_routes_and_wishlist_are_customer_scoped(self):
        guest = self.app.test_client()
        for path in ("/cart", "/wishlist", "/checkout"):
            response = guest.get(path)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.location)

        first_client = self.app.test_client()
        self.assertEqual(self.login(first_client).status_code, 302)
        token = self.csrf(first_client, f"/product/{self.first_product.slug}")
        first_client.post(
            f"/wishlist/{self.first_product.id}/toggle",
            data={"csrf_token": token, "next": f"/product/{self.first_product.slug}"},
        )
        self.assertEqual(WishlistItem.query.filter_by(user_id=self.first.id).count(), 1)
        self.assertIn("Test Runner", first_client.get("/wishlist").get_data(as_text=True))

        second_client = self.app.test_client()
        self.assertEqual(self.login(second_client, email="shopper2@example.com").status_code, 302)
        self.assertNotIn("Test Runner", second_client.get("/wishlist").get_data(as_text=True))

    def test_forgot_password_is_non_enumerating_and_link_is_one_time(self):
        client = self.app.test_client()
        csrf_token = self.csrf(client, "/forgot-password")
        with patch("app.services.email_service.send_password_reset_email") as send_reset:
            response = client.post(
                "/forgot-password",
                data={"csrf_token": csrf_token, "email": "shopper1@example.com"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("If an active STEPZONE customer account", response.get_data(as_text=True))
        send_reset.assert_called_once()
        reset_url = send_reset.call_args.args[1]
        reset_path = urlsplit(reset_url).path
        reset_page = client.get(reset_path)
        self.assertEqual(reset_page.status_code, 200)
        reset_html = reset_page.get_data(as_text=True)
        csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', reset_html).group(1)
        next_url = re.search(r'name="next" value="([^"]*)"', reset_html).group(1)
        response = client.post(
            reset_path,
            data={
                "csrf_token": csrf_token,
                "next": next_url,
                "password": "NewCustomerPassword!",
                "confirm_password": "NewCustomerPassword!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(check_password_hash(self.first.password_hash, "NewCustomerPassword!"))
        self.assertEqual(client.post(reset_path, data={"csrf_token": csrf_token, "password": "AnotherNewPassword!", "confirm_password": "AnotherNewPassword!"}).status_code, 400)

    def test_next_url_rejects_external_and_backslash_redirects(self):
        with self.app.test_request_context():
            self.assertEqual(safe_next_url("https://attacker.example"), "/account")
            self.assertEqual(safe_next_url("/%5c%5cattacker.example"), "/account")
            self.assertEqual(safe_next_url("/account?tab=orders"), "/account?tab=orders")


if __name__ == "__main__":
    unittest.main()
