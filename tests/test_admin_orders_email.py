import re
import unittest
from decimal import Decimal
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Brand, Category, Order, OrderItem, Payment, Product, ProductVariant, User
from app.services.email_service import send_order_confirmation
from config import config_by_name


TestingConfig = type(
    "TestingConfig",
    (),
    {
        "SECRET_KEY": "test-secret-orders",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,
        "BREVO_API_KEY": "test-key",
        "BREVO_SENDER_EMAIL": "test@example.com",
        "BREVO_SENDER_NAME": "STEPZONE",
    },
)
config_by_name["order_testing"] = TestingConfig


class AdminOrderAndEmailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("order_testing")
        cls.context = cls.app.app_context()
        cls.context.push()
        db.create_all()
        brand = Brand(name="Order Brand", slug="order-brand")
        category = Category(name="Order Category", slug="order-category")
        product = Product(name="Order Sneaker", slug="order-sneaker", brand=brand, category=category, base_price=Decimal("5000.00"))
        variant = ProductVariant(product=product, sku="ORDER-08", size="8", color="Black", stock_quantity=4, price=Decimal("5000.00"))
        admin = User(email="orders-admin@example.com", password_hash=generate_password_hash("CorrectHorseBatteryStaple!"), first_name="Orders", last_name="Admin", role="admin")
        cls.variant = variant
        db.session.add_all([brand, category, product, variant, admin])
        db.session.flush()
        cls.order = Order(order_number="SZ-ORDER-TEST", checkout_token="order-test-token", status="pending", payment_method="cod", payment_status="pending_cod", subtotal=Decimal("5000.00"), shipping_fee=Decimal("0"), total_amount=Decimal("5000.00"), customer_name="Order Customer", customer_email="order@example.com", customer_phone="9999999999", shipping_address="Order Address", shipping_city="City", shipping_state="State", shipping_postal_code="000000")
        cls.order.items.append(OrderItem(product=product, product_variant=variant, product_name=product.name, sku=variant.sku, size=variant.size, color=variant.color, unit_price=Decimal("5000.00"), quantity=1, line_total=Decimal("5000.00")))
        cls.order.payment = Payment(provider="cod", provider_order_id=cls.order.order_number, amount=Decimal("5000.00"), status="cod_pending")
        db.session.add(cls.order)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.context.pop()

    def setUp(self):
        self.client = self.app.test_client()
        login = self.client.get("/admin/login")
        csrf = re.search(r'name="csrf_token" value="([^"]+)"', login.get_data(as_text=True)).group(1)
        self.client.post("/admin/login", data={"csrf_token": csrf, "email": "orders-admin@example.com", "password": "CorrectHorseBatteryStaple!"})
        dashboard = self.client.get("/admin/")
        self.csrf = re.search(r'name="csrf_token" value="([^"]+)"', dashboard.get_data(as_text=True)).group(1)

    def test_order_authorization_listing_and_details(self):
        self.assertEqual(self.app.test_client().get("/admin/orders").status_code, 302)
        self.assertEqual(self.client.get("/admin/orders").status_code, 200)
        detail = self.client.get(f"/admin/orders/{self.order.id}")
        self.assertEqual(detail.status_code, 200)
        self.assertIn(self.order.order_number, detail.get_data(as_text=True))

    def test_order_search_escapes_wildcards_and_listing_paginates_25_rows(self):
        special = []
        for index in range(26):
            order = Order(
                order_number=f"SZ-PAGE-{index:02d}", checkout_token=f"page-token-{index:02d}",
                status="confirmed", payment_method="cod", payment_status="pending_cod",
                subtotal=Decimal("100"), shipping_fee=Decimal("0"), total_amount=Decimal("100"),
                customer_name="Customer 100%_match" if index == 0 else "Customer 100Xmatch",
                customer_email=f"page-{index}@example.com", customer_phone="9999999999",
                shipping_address="Address", shipping_city="City", shipping_state="State", shipping_postal_code="000000",
            )
            order.payment = Payment(provider="cod", provider_order_id=order.order_number, amount=order.total_amount, status="cod_pending")
            special.append(order)
        db.session.add_all(special)
        db.session.commit()

        literal = self.client.get("/admin/orders?search=%25_").get_data(as_text=True)
        self.assertIn("SZ-PAGE-00", literal)
        self.assertNotIn("SZ-PAGE-01", literal)
        first = self.client.get("/admin/orders?search=SZ-PAGE-")
        self.assertIn("Page 1 of 2", first.get_data(as_text=True))
        second = self.client.get("/admin/orders?search=SZ-PAGE-&page=2")
        self.assertIn("Page 2 of 2", second.get_data(as_text=True))
        self.assertIn("search=SZ-PAGE-", second.get_data(as_text=True))

    def test_safe_status_transitions(self):
        confirmed = self.client.post(f"/admin/orders/{self.order.id}/status", data={"csrf_token": self.csrf, "status": "confirmed"})
        self.assertEqual(confirmed.status_code, 302)
        db.session.refresh(self.order)
        self.assertEqual(self.order.status, "confirmed")
        invalid = self.client.post(f"/admin/orders/{self.order.id}/status", data={"csrf_token": self.csrf, "status": "delivered"})
        self.assertEqual(invalid.status_code, 400)
        db.session.refresh(self.order)
        self.assertEqual(self.order.payment_status, "pending_cod")

    def test_cancellation_restores_paid_or_reserved_stock_once_and_marks_refund_pending(self):
        paid = Order(
            order_number="SZ-CANCEL-PAID", checkout_token="cancel-paid-token", status="confirmed",
            payment_method="cod", payment_status="paid", stock_deducted=True,
            subtotal=Decimal("10000"), shipping_fee=Decimal("0"), total_amount=Decimal("10000"),
            customer_name="Paid Customer", customer_email="paid@example.com", customer_phone="9999999999",
            shipping_address="Address", shipping_city="City", shipping_state="State", shipping_postal_code="000000",
        )
        paid.items.append(OrderItem(product_id=self.order.items[0].product_id, product_variant_id=self.variant.id, product_name="Order Sneaker", sku=self.variant.sku, size=self.variant.size, color=self.variant.color, unit_price=Decimal("5000"), quantity=2, line_total=Decimal("10000")))
        paid.payment = Payment(provider="paytm", provider_order_id=paid.order_number, amount=paid.total_amount, status="success")
        pending = Order(
            order_number="SZ-CANCEL-PENDING", checkout_token="cancel-pending-token", status="pending",
            payment_method="paytm", payment_status="pending", stock_reserved=True,
            subtotal=Decimal("5000"), shipping_fee=Decimal("0"), total_amount=Decimal("5000"),
            customer_name="Pending Customer", customer_email="pending@example.com", customer_phone="9999999999",
            shipping_address="Address", shipping_city="City", shipping_state="State", shipping_postal_code="000000",
        )
        pending.items.append(OrderItem(product_id=self.order.items[0].product_id, product_variant_id=self.variant.id, product_name="Order Sneaker", sku=self.variant.sku, size=self.variant.size, color=self.variant.color, unit_price=Decimal("5000"), quantity=1, line_total=Decimal("5000")))
        pending.payment = Payment(provider="paytm", provider_order_id=pending.order_number, amount=pending.total_amount, status="pending")
        self.variant.stock_quantity = 1
        db.session.add_all([paid, pending])
        db.session.commit()

        first = self.client.post(f"/admin/orders/{paid.id}/status", data={"csrf_token": self.csrf, "status": "cancelled"})
        self.assertEqual(first.status_code, 302)
        db.session.refresh(paid)
        db.session.refresh(self.variant)
        self.assertEqual(paid.payment_status, "refund_pending")
        self.assertEqual(paid.payment.status, "refund_pending")
        self.assertFalse(paid.stock_deducted)
        self.assertEqual(self.variant.stock_quantity, 3)
        repeated = self.client.post(f"/admin/orders/{paid.id}/status", data={"csrf_token": self.csrf, "status": "cancelled"})
        self.assertEqual(repeated.status_code, 400)
        db.session.refresh(self.variant)
        self.assertEqual(self.variant.stock_quantity, 3)

        second = self.client.post(f"/admin/orders/{pending.id}/status", data={"csrf_token": self.csrf, "status": "cancelled"})
        self.assertEqual(second.status_code, 302)
        db.session.refresh(self.variant)
        db.session.refresh(pending)
        self.assertFalse(pending.stock_reserved)
        self.assertEqual(self.variant.stock_quantity, 4)

    def test_email_success_and_duplicate_prevention(self):
        calls = []
        with patch("app.services.email_service._send_brevo", side_effect=lambda **kwargs: calls.append(kwargs)):
            self.assertTrue(send_order_confirmation(self.order.id))
            self.assertFalse(send_order_confirmation(self.order.id))
        db.session.refresh(self.order.payment)
        self.assertEqual(self.order.payment.email_status, "sent")
        self.assertEqual(len(calls), 1)

    def test_email_failure_does_not_change_order(self):
        original_status = self.order.status
        self.order.payment.email_status = "pending"
        db.session.commit()
        with patch("app.services.email_service._send_brevo", side_effect=RuntimeError("mail unavailable")):
            self.assertFalse(send_order_confirmation(self.order.id))
        db.session.refresh(self.order)
        self.assertEqual(self.order.status, original_status)
        self.assertEqual(self.order.payment.email_status, "failed")

    def test_retry_failed_emails_cli_retries_with_brevo_mock(self):
        Payment.query.update({Payment.email_status: "sent"})
        self.order.payment.email_status = "failed"
        db.session.commit()
        with patch("app.services.email_service._send_brevo", return_value={"messageId": "mocked"}) as send_brevo:
            result = self.app.test_cli_runner().invoke(args=["retry-failed-emails"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("1 sent successfully", result.output)
        send_brevo.assert_called_once()
        db.session.refresh(self.order.payment)
        self.assertEqual(self.order.payment.email_status, "sent")


if __name__ == "__main__":
    unittest.main()
