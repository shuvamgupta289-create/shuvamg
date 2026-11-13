import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch

from app import create_app
from app.extensions import db
from app.models import Brand, Category, Order, OrderItem, Payment, Product, ProductVariant
from app.services.order_service import create_pending_order, mark_order_cod, mark_order_failed
from config import config_by_name
from config import PAYTM_GATEWAY_ENDPOINTS


PaymentTestingConfig = type(
    "PaymentTestingConfig",
    (),
    {
        "SECRET_KEY": "payment-test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,
        "PAYTM_MID": "test-mid",
        "PAYTM_MERCHANT_KEY": "test-key",
        "PAYTM_WEBSITE": "test-website",
        "PAYTM_ENVIRONMENT": "staging",
    },
)
config_by_name["payment_testing"] = PaymentTestingConfig


class CheckoutPaymentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("payment_testing")
        cls.context = cls.app.app_context()
        cls.context.push()
        db.create_all()
        cls.brand = Brand(name="Payment Brand", slug="payment-brand")
        cls.category = Category(name="Payment Shoes", slug="payment-shoes")
        cls.product = Product(
            name="Payment Runner", slug="payment-runner", brand=cls.brand,
            category=cls.category, base_price=Decimal("500.00"),
        )
        cls.variant = ProductVariant(
            product=cls.product, sku="PAYMENT-RUNNER-8", size="8", color="Black",
            price=Decimal("500.00"), stock_quantity=5,
        )
        db.session.add_all([cls.brand, cls.category, cls.product, cls.variant])
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
        self.variant.stock_quantity = 5
        self.variant.is_active = True
        self.product.is_active = True
        db.session.commit()

    def make_order(self, *, quantity=2, token="payment-token"):
        return create_pending_order(
            payment_method="paytm",
            customer={
                "name": "Payment Customer", "email": "pay@example.com", "phone": "9999999999",
                "address": "1 Test Road", "city": "Pune", "state": "MH", "postal_code": "411001",
            },
            checkout_token=token,
            items=[{"variant_id": self.variant.id, "product_id": self.product.id, "quantity": quantity}],
        )

    def test_paytm_order_reserves_stock_and_failure_releases_it_once(self):
        order = self.make_order()
        self.assertEqual(self.variant.stock_quantity, 3)
        self.assertTrue(order.stock_reserved)

        mark_order_failed(order, "Paytm declined the payment.")
        db.session.commit()
        self.assertEqual(self.variant.stock_quantity, 5)
        self.assertFalse(order.stock_reserved)
        self.assertEqual(order.payment_status, "failed")

        mark_order_failed(order, "replayed failure")
        db.session.commit()
        self.assertEqual(self.variant.stock_quantity, 5)

    def test_duplicate_checkout_token_returns_existing_order_without_deducting_twice(self):
        order = create_pending_order(
            payment_method="cod",
            customer={"name":"A", "email":"a@example.com", "phone":"9999999999", "address":"X", "city":"Y", "state":"Z", "postal_code":"1"},
            checkout_token="cod-duplicate-token",
            items=[{"variant_id":self.variant.id, "product_id":self.product.id, "quantity":2}],
        )
        mark_order_cod(order)
        db.session.commit()
        stock_after_first = self.variant.stock_quantity
        replay = create_pending_order(
            payment_method="cod",
            customer={"name":"A", "email":"a@example.com", "phone":"9999999999", "address":"X", "city":"Y", "state":"Z", "postal_code":"1"},
            checkout_token="cod-duplicate-token",
            items=[{"variant_id":self.variant.id, "product_id":self.product.id, "quantity":2}],
        )
        self.assertEqual(replay.id, order.id)
        self.assertEqual(self.variant.stock_quantity, stock_after_first)

    def test_callback_success_consumes_reservation_and_replay_does_not_repeat_email(self):
        order = self.make_order()
        db.session.commit()
        callback = {"ORDERID": order.order_number}
        result = ({"resultStatus": "TXN_SUCCESS", "resultCode": "01", "resultMsg": "Success"}, {"txnAmount": "1000.00", "txnId": "TXN-1"})
        with patch("app.routes.checkout.verify_callback", return_value=True), patch("app.routes.checkout.verify_payment", return_value=result), patch("app.routes.checkout.send_order_confirmation") as email:
            first = self.app.test_client().post("/payment/paytm/callback", data=callback)
            replay = self.app.test_client().post("/payment/paytm/callback", data=callback)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(replay.status_code, 200)
        db.session.refresh(order)
        db.session.refresh(self.variant)
        self.assertEqual(self.variant.stock_quantity, 3)
        self.assertFalse(order.stock_reserved)
        self.assertTrue(order.stock_deducted)
        self.assertEqual(order.payment_status, "paid")
        email.assert_called_once_with(order.id)

    def test_successful_charge_without_inventory_is_marked_for_review(self):
        order = self.make_order()
        db.session.commit()
        order.stock_reserved = False  # Simulate a legacy pending order without a reservation.
        self.variant.stock_quantity = 0
        db.session.commit()
        result = ({"resultStatus": "TXN_SUCCESS", "resultCode": "01", "resultMsg": "Success"}, {"txnAmount": "1000.00", "txnId": "TXN-2"})
        with patch("app.routes.checkout.verify_callback", return_value=True), patch("app.routes.checkout.verify_payment", return_value=result), patch("app.routes.checkout.send_order_confirmation") as email:
            response = self.app.test_client().post("/payment/paytm/callback", data={"ORDERID": order.order_number})

        self.assertEqual(response.status_code, 200)
        self.assertIn("payment was received", response.get_data(as_text=True).lower())
        db.session.refresh(order)
        self.assertEqual(order.status, "paid_needs_review")
        self.assertEqual(order.payment_status, "paid_needs_review")
        self.assertEqual(order.payment.status, "paid_needs_review")
        email.assert_not_called()

    def test_non_success_callback_releases_reserved_stock(self):
        order = self.make_order()
        db.session.commit()
        result = ({"resultStatus": "TXN_FAILURE", "resultCode": "227", "resultMsg": "Declined"}, {"txnAmount": "1000.00"})
        with patch("app.routes.checkout.verify_callback", return_value=True), patch("app.routes.checkout.verify_payment", return_value=result):
            response = self.app.test_client().post("/payment/paytm/callback", data={"ORDERID": order.order_number})

        self.assertEqual(response.status_code, 200)
        db.session.refresh(order)
        db.session.refresh(self.variant)
        self.assertEqual(order.payment_status, "failed")
        self.assertFalse(order.stock_reserved)
        self.assertEqual(self.variant.stock_quantity, 5)

    def test_bad_callback_checksum_does_not_change_pending_order_or_release_stock(self):
        order = self.make_order()
        db.session.commit()
        with patch("app.routes.checkout.verify_callback", return_value=False):
            response = self.app.test_client().post("/payment/paytm/callback", data={"ORDERID": order.order_number})
        self.assertEqual(response.status_code, 400)
        db.session.refresh(order)
        db.session.refresh(self.variant)
        self.assertEqual(order.payment_status, "pending")
        self.assertTrue(order.stock_reserved)
        self.assertEqual(self.variant.stock_quantity, 3)

    def test_successful_charge_with_amount_mismatch_is_marked_for_review(self):
        order = self.make_order()
        db.session.commit()
        result = ({"resultStatus": "TXN_SUCCESS", "resultCode": "01", "resultMsg": "Success"}, {"txnAmount": "999.00", "txnId": "TXN-MISMATCH"})
        with patch("app.routes.checkout.verify_callback", return_value=True), patch("app.routes.checkout.verify_payment", return_value=result), patch("app.routes.checkout.send_order_confirmation") as email:
            response = self.app.test_client().post("/payment/paytm/callback", data={"ORDERID": order.order_number})
        self.assertEqual(response.status_code, 200)
        self.assertIn("needs manual review before fulfillment", response.get_data(as_text=True).lower())
        db.session.refresh(order)
        self.assertEqual(order.payment_status, "paid_needs_review")
        self.assertTrue(order.stock_reserved)
        email.assert_not_called()

    def test_paytm_timeout_keeps_reservation_and_returns_non_503_review_message(self):
        order = self.make_order()
        db.session.commit()
        with patch("app.routes.checkout.verify_callback", return_value=True), patch("app.routes.checkout.verify_payment", side_effect=TimeoutError("mock timeout")):
            response = self.app.test_client().post("/payment/paytm/callback", data={"ORDERID": order.order_number})
        self.assertEqual(response.status_code, 200)
        self.assertIn("status under review", response.get_data(as_text=True).lower())
        db.session.refresh(order)
        db.session.refresh(self.variant)
        self.assertEqual(order.payment_status, "pending")
        self.assertTrue(order.stock_reserved)
        self.assertEqual(self.variant.stock_quantity, 3)

    def test_two_buyers_cannot_reserve_the_last_pair(self):
        self.variant.stock_quantity = 2
        db.session.commit()
        first = self.make_order(quantity=2, token="last-pair-first")
        self.assertEqual(self.variant.stock_quantity, 0)
        with self.assertRaisesRegex(ValueError, "not available|enough stock"):
            self.make_order(quantity=1, token="last-pair-second")
        db.session.commit()
        self.assertEqual(Order.query.filter_by(checkout_token="last-pair-first").count(), 1)
        self.assertEqual(Order.query.filter_by(checkout_token="last-pair-second").count(), 0)
        self.assertEqual(self.variant.stock_quantity, 0)

    def test_expire_pending_orders_cli_releases_stale_reservations(self):
        order = self.make_order()
        order.created_at = datetime.now(timezone.utc) - timedelta(minutes=45)
        db.session.commit()

        result = self.app.test_cli_runner().invoke(args=["expire-pending-orders", "--minutes", "30"])

        self.assertEqual(result.exit_code, 0, result.output)
        db.session.refresh(order)
        db.session.refresh(self.variant)
        self.assertEqual(order.payment_status, "expired")
        self.assertFalse(order.stock_reserved)
        self.assertEqual(self.variant.stock_quantity, 5)

    def test_paytm_environment_selects_staging_or_production_gateway_urls(self):
        self.assertIn("securegw-stage.paytm.in", PAYTM_GATEWAY_ENDPOINTS["staging"]["PAYTM_INITIATE_URL"])
        self.assertIn("securegw-stage.paytm.in", PAYTM_GATEWAY_ENDPOINTS["staging"]["PAYTM_STATUS_URL"])
        self.assertIn("securegw.paytm.in", PAYTM_GATEWAY_ENDPOINTS["production"]["PAYTM_INITIATE_URL"])
        self.assertIn("securegw.paytm.in", PAYTM_GATEWAY_ENDPOINTS["production"]["PAYTM_STATUS_URL"])


if __name__ == "__main__":
    unittest.main()
