import io
import json
import types
import unittest
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from flask import Flask

from app.services.email_service import EmailConfigurationError, _send_brevo, send_password_reset_email
from app.services.paytm_service import (
    PaytmConfigurationError,
    PaytmGatewayError,
    _checksum,
    _post_json,
    _settings,
    initiate_transaction,
    verify_callback,
    verify_payment,
)


class PaymentServiceTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__, template_folder="../app/templates")
        self.app.config.update(
            SECRET_KEY="service-test-secret",
            PAYTM_MID="test-mid",
            PAYTM_MERCHANT_KEY="test-merchant-key",
            PAYTM_WEBSITE="test-website",
            PAYTM_ENVIRONMENT="staging",
            PAYTM_CALLBACK_URL="https://stepzone.example/payment/paytm/callback",
            PAYTM_INITIATE_URL="https://paytm.example/initiate",
            PAYTM_STATUS_URL="https://paytm.example/status",
            BREVO_API_KEY="test-brevo-key",
            BREVO_SENDER_EMAIL="sender@example.com",
            BREVO_SENDER_NAME="STEPZONE Test",
        )

    def test_paytm_settings_validate_keys_and_environment(self):
        with self.app.app_context():
            self.assertEqual(_settings()["PAYTM_ENVIRONMENT"], "staging")
            self.app.config["PAYTM_MID"] = ""
            with self.assertRaises(PaytmConfigurationError):
                _settings()
            self.app.config["PAYTM_MID"] = "test-mid"
            self.app.config["PAYTM_ENVIRONMENT"] = "sandbox"
            with self.assertRaisesRegex(PaytmConfigurationError, "staging or production"):
                _settings()

    def test_checksum_and_callback_signature_use_mocked_paytmchecksum(self):
        fake_checksum = types.ModuleType("paytmchecksum")
        fake_checksum.PaytmChecksum = SimpleNamespace(
            generateSignature=lambda payload, key: f"signature-{key}",
            verifySignature=lambda payload, key, signature: signature == f"signature-{key}",
        )
        with self.app.app_context(), patch.dict("sys.modules", {"paytmchecksum": fake_checksum}):
            self.assertEqual(_checksum({"orderId": "SZ-1"}), "signature-test-merchant-key")
            self.assertFalse(verify_callback({}))
            self.assertTrue(verify_callback({"CHECKSUMHASH": "signature-test-merchant-key"}))

    def test_initiate_transaction_uses_mock_gateway_and_rejects_unsuccessful_init(self):
        order = SimpleNamespace(id=8, order_number="SZ-MOCK-8", total_amount=Decimal("1250.00"), currency="INR")
        success = {"body": {"resultInfo": {"resultStatus": "S"}, "txnToken": "mock-token"}}
        with self.app.app_context(), patch("app.services.paytm_service._checksum", return_value="mock-signature") as checksum, patch("app.services.paytm_service._post_json", return_value=success) as post:
            result = initiate_transaction(order)
        self.assertEqual(result, {"order_id": "SZ-MOCK-8", "txn_token": "mock-token"})
        self.assertEqual(post.call_args.args[0], "https://paytm.example/initiate")
        checksum.assert_called_once()

        failure = {"body": {"resultInfo": {"resultStatus": "F"}}}
        with self.app.app_context(), patch("app.services.paytm_service._checksum", return_value="mock-signature"), patch("app.services.paytm_service._post_json", return_value=failure):
            with self.assertRaises(PaytmGatewayError):
                initiate_transaction(order)

    def test_verify_payment_uses_mock_gateway(self):
        response = {"body": {"resultInfo": {"resultStatus": "TXN_SUCCESS"}, "txnAmount": "10.00"}}
        with self.app.app_context(), patch("app.services.paytm_service._checksum", return_value="sig"), patch("app.services.paytm_service._post_json", return_value=response) as post:
            result_info, status = verify_payment("SZ-VERIFY")
        self.assertEqual(result_info["resultStatus"], "TXN_SUCCESS")
        self.assertEqual(status["txnAmount"], "10.00")
        self.assertEqual(post.call_args.args[0], "https://paytm.example/status")

    def test_json_http_helper_decodes_mock_response_without_network(self):
        with patch("app.services.paytm_service.urlopen", return_value=io.BytesIO(b'{"body":{"ok":true}}')) as open_url:
            payload = _post_json("https://paytm.example/status", {"test": True}, params={"mid": "mock"})
        self.assertTrue(payload["body"]["ok"])
        self.assertIn("mid=mock", open_url.call_args.args[0].full_url)

    def test_brevo_payload_and_password_reset_use_mock_transport(self):
        with self.app.app_context(), patch("app.services.email_service.urlopen", return_value=io.BytesIO(b'{"messageId":"mock"}')) as open_url:
            result = _send_brevo(
                recipient_email="customer@example.com", recipient_name="Customer", subject="Test",
                html_content="<p>Test</p>", text_content="Test", message_id="mock-id",
            )
        self.assertEqual(result["messageId"], "mock")
        payload = json.loads(open_url.call_args.args[0].data)
        self.assertEqual(payload["to"][0]["email"], "customer@example.com")
        user = SimpleNamespace(id=2, first_name="Test", last_name="Customer", email="customer@example.com")
        with self.app.app_context(), patch("app.services.email_service._send_brevo") as send:
            self.assertTrue(send_password_reset_email(user, "https://stepzone.example/reset/mock"))
        send.assert_called_once()

    def test_brevo_missing_configuration_fails_without_network(self):
        self.app.config["BREVO_API_KEY"] = None
        with self.app.app_context():
            with self.assertRaises(EmailConfigurationError):
                _send_brevo(
                    recipient_email="customer@example.com", recipient_name="Customer", subject="Test",
                    html_content="", text_content="", message_id="mock-id",
                )


if __name__ == "__main__":
    unittest.main()
