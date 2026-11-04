from datetime import datetime
import secrets
import json
from urllib.request import Request, urlopen

from flask import current_app, render_template
from sqlalchemy import select

from ..extensions import db
from ..models import Order, Payment


class EmailConfigurationError(RuntimeError):
    pass


def _send_brevo(*, recipient_email, recipient_name, subject, html_content, text_content, message_id):
    api_key = current_app.config.get("BREVO_API_KEY")
    sender_email = current_app.config.get("BREVO_SENDER_EMAIL")
    if not api_key or not sender_email:
        raise EmailConfigurationError("Brevo email configuration is incomplete.")
    payload = {
        "sender": {"name": current_app.config.get("BREVO_SENDER_NAME", "STEPZONE"), "email": sender_email},
        "to": [{"email": recipient_email, "name": recipient_name}],
        "subject": subject,
        "htmlContent": html_content,
        "textContent": text_content,
        "headers": {"X-STEPZONE-Message-ID": message_id},
    }
    request = Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(payload).encode("utf-8"),
        headers={"accept": "application/json", "api-key": api_key, "content-type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def send_password_reset_email(user, reset_url):
    recipient_name = f"{user.first_name} {user.last_name}".strip()
    _send_brevo(
        recipient_email=user.email,
        recipient_name=recipient_name,
        subject="Reset your STEPZONE password",
        html_content=render_template("emails/password_reset.html", user=user, reset_url=reset_url),
        text_content=render_template("emails/password_reset.txt", user=user, reset_url=reset_url),
        message_id=f"stepzone-password-reset-{user.id}-{secrets.token_hex(8)}",
    )
    return True


def send_order_confirmation(order_id):
    with current_app.app_context():
        payment = db.session.execute(
            select(Payment).where(Payment.order_id == order_id).with_for_update()
        ).scalar_one_or_none()
        if payment is None or payment.email_status in {"sent", "sending"}:
            return False
        payment.email_status = "sending"
        payment.email_error = None
        db.session.commit()

        order = db.session.get(Order, order_id)
        if order is None:
            return False
        subject = f"STEPZONE order confirmation {order.order_number}"
        message_id = f"stepzone-order-{order.order_number}"
        try:
            html_content = render_template("emails/order_confirmation.html", order=order)
            text_content = render_template("emails/order_confirmation.txt", order=order)
            _send_brevo(
                recipient_email=order.customer_email,
                recipient_name=order.customer_name,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                message_id=message_id,
            )
        except Exception as error:
            payment = db.session.get(Payment, payment.id)
            payment.email_status = "failed"
            payment.email_error = type(error).__name__
            db.session.commit()
            return False

        payment = db.session.get(Payment, payment.id)
        payment.email_status = "sent"
        payment.email_sent_at = datetime.utcnow()
        payment.email_error = None
        db.session.commit()
        return True
