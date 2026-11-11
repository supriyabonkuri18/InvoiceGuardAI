
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")

PAYPAL_BASE_URL = os.getenv(
    "PAYPAL_BASE_URL",
    "https://api-m.sandbox.paypal.com"
)


def get_access_token():
    """
    Authenticate with PayPal and obtain an OAuth access token.
    """

    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        raise ValueError("PayPal credentials are missing from .env")

    response = requests.post(
        f"{PAYPAL_BASE_URL}/v1/oauth2/token",
        auth=HTTPBasicAuth(
            PAYPAL_CLIENT_ID,
            PAYPAL_CLIENT_SECRET
        ),
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US"
        },
        data={
            "grant_type": "client_credentials"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()["access_token"]

def create_paypal_order(
    amount,
    invoice_number,
    return_url,
    cancel_url,
    currency="USD"
):
    """
    Create a PayPal checkout order.
    Returns the order ID and approval URL.
    """

    if float(amount) <= 0:
        raise ValueError("Payment amount must be greater than zero.")

    access_token = get_access_token()

    url = f"{PAYPAL_BASE_URL}/v2/checkout/orders"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": str(invoice_number),
                "custom_id": str(invoice_number),
                "description": f"InvoiceGuard payment - {invoice_number}",
                "amount": {
                    "currency_code": currency,
                    "value": f"{float(amount):.2f}"
                }
            }
        ],
        "application_context": {
            "brand_name": "InvoiceGuard AI",
            "user_action": "PAY_NOW",
            "return_url": return_url,
            "cancel_url": cancel_url
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    order = response.json()

    approval_url = next(
        (
            link["href"]
            for link in order.get("links", [])
            if link.get("rel") == "approve"
        ),
        None
    )

    if not approval_url:
        raise RuntimeError("PayPal approval URL was not returned.")

    return {
        "order_id": order["id"],
        "approval_url": approval_url,
        "status": order["status"]
    }

def capture_paypal_order(order_id):

    access_token = get_access_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    # Retrieve original order details before capture
    order_url = f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}"

    order_response = requests.get(
        order_url,
        headers=headers,
        timeout=30
    )

    order_response.raise_for_status()

    original_order = order_response.json()

    purchase_units = original_order.get("purchase_units", [])
    original_unit = purchase_units[0] if purchase_units else {}

    invoice_number = (
        original_unit.get("custom_id")
        or original_unit.get("reference_id")
    )

    # Capture the approved PayPal order
    capture_url = f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture"

    response = requests.post(
        capture_url,
        headers=headers,
        json={},
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    captured_units = result.get("purchase_units", [])
    captured_unit = captured_units[0] if captured_units else {}

    captures = (
        captured_unit
        .get("payments", {})
        .get("captures", [])
    )

    capture_details = captures[0] if captures else {}
    captured_amount = capture_details.get("amount", {})

    # Fallback to capture response if needed
    invoice_number = (
        invoice_number
        or captured_unit.get("custom_id")
        or captured_unit.get("reference_id")
    )

    return {
        "order_id": result.get("id"),
        "status": result.get("status"),
        "capture_id": capture_details.get("id"),
        "invoice_number": invoice_number,
        "amount": float(captured_amount.get("value", 0)),
        "currency": captured_amount.get("currency_code"),
        "details": result
    }