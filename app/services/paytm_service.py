from decimal import Decimal
import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode

from flask import current_app


class PaytmConfigurationError(RuntimeError):
    pass


class PaytmGatewayError(RuntimeError):
    pass


def _settings():
    required = ("PAYTM_MID", "PAYTM_MERCHANT_KEY", "PAYTM_WEBSITE", "PAYTM_ENVIRONMENT")
    settings = {key: current_app.config.get(key) for key in required}
    missing = [key for key, value in settings.items() if not value]
    if missing:
        raise PaytmConfigurationError("Paytm staging configuration is incomplete.")
    if settings["PAYTM_ENVIRONMENT"] != "staging":
        raise PaytmConfigurationError("Only Paytm staging is enabled.")
    return settings


def _checksum(payload):
    try:
        from paytmchecksum import PaytmChecksum
    except ImportError as error:
        raise PaytmConfigurationError("The Paytm checksum dependency is not installed.") from error
    return PaytmChecksum.generateSignature(payload, _settings()["PAYTM_MERCHANT_KEY"])


def verify_callback(payload):
    settings = _settings()
    checksum = payload.get("CHECKSUMHASH")
    if not checksum:
        return False
    from paytmchecksum import PaytmChecksum
    return PaytmChecksum.verifySignature(payload, settings["PAYTM_MERCHANT_KEY"], checksum)


def _post_json(url, payload, params=None):
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def initiate_transaction(order):
    settings = _settings()
    payload = {
        "body": {
            "requestType": "Payment",
            "mid": settings["PAYTM_MID"],
            "websiteName": settings["PAYTM_WEBSITE"],
            "orderId": order.order_number,
            "txnAmount": {"value": str(Decimal(order.total_amount)), "currency": order.currency},
            "userInfo": {"custId": f"STEPZONE-{order.id}"},
            "callbackUrl": current_app.config["PAYTM_CALLBACK_URL"],
        },
    }
    payload["head"] = {"signature": _checksum(payload["body"])}
    data = _post_json(
        current_app.config["PAYTM_INITIATE_URL"],
        payload,
        params={"mid": settings["PAYTM_MID"], "orderId": order.order_number},
    )
    result_info = data.get("body", {}).get("resultInfo", {})
    txn_token = data.get("body", {}).get("txnToken")
    if result_info.get("resultStatus") != "S" or not txn_token:
        raise PaytmGatewayError("Paytm transaction initiation was not successful.")
    return {"order_id": order.order_number, "txn_token": txn_token}


def verify_payment(order_number):
    settings = _settings()
    body = {"mid": settings["PAYTM_MID"], "orderId": order_number}
    payload = {"body": body, "head": {"signature": _checksum(body)}}
    data = _post_json(current_app.config["PAYTM_STATUS_URL"], payload).get("body", {})
    return data.get("resultInfo", {}), data
