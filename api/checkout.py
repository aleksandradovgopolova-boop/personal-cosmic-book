from __future__ import annotations

import base64
import json
import os
import ssl
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, Optional


# Product catalogue (mirrors lib/products.ts). Amounts are in whole rubles.
PRODUCTS = {
    "pcb_basic": {"title": "Полная книга", "amount": 990},
    "pcb_bundle": {"title": "Подарочная книга", "amount": 990},
    "pcb_compatibility": {"title": "Книга пары", "amount": 1490},
}

YOOKASSA_API = "https://api.yookassa.ru/v3/payments"


def create_checkout(payload: Dict[str, Any]) -> Dict[str, Any]:
    product_id = str(payload.get("product") or "pcb_basic")
    product = PRODUCTS.get(product_id)
    if not product:
        raise ValueError("unknown product")

    email = str(payload.get("email") or "").strip()
    if not email:
        raise ValueError("email is required")

    return_url = str(payload.get("return_url") or os.environ.get("NEXT_PUBLIC_APP_URL") or "")

    shop_id = os.environ.get("YOOKASSA_SHOP_ID")
    secret_key = os.environ.get("YOOKASSA_SECRET_KEY")

    # No payment credentials configured — return a demo confirmation so the flow
    # is fully exercisable without a live provider.
    if not shop_id or not secret_key:
        return {
            "status": "demo",
            "product": product_id,
            "amount": product["amount"],
            "currency": "RUB",
            "message": "Демо-оплата: платёжный провайдер ещё не подключён. Книга будет отправлена на почту после реальной оплаты.",
        }

    payment = _create_yookassa_payment(
        shop_id=shop_id,
        secret_key=secret_key,
        amount=product["amount"],
        description=f"{product['title']} — Personal Cosmic Book",
        email=email,
        return_url=return_url,
    )

    confirmation = payment.get("confirmation") or {}
    return {
        "status": payment.get("status", "pending"),
        "product": product_id,
        "amount": product["amount"],
        "currency": "RUB",
        "payment_id": payment.get("id"),
        "confirmation_url": confirmation.get("confirmation_url"),
    }


def _create_yookassa_payment(
    shop_id: str,
    secret_key: str,
    amount: int,
    description: str,
    email: str,
    return_url: str,
) -> Dict[str, Any]:
    body = {
        "amount": {"value": f"{amount}.00", "currency": "RUB"},
        "capture": True,
        "description": description,
        "confirmation": {"type": "redirect", "return_url": return_url or "https://example.com"},
        "receipt": {
            "customer": {"email": email},
            "items": [
                {
                    "description": description,
                    "quantity": "1.00",
                    "amount": {"value": f"{amount}.00", "currency": "RUB"},
                    "vat_code": 1,
                }
            ],
        },
    }

    token = base64.b64encode(f"{shop_id}:{secret_key}".encode("utf-8")).decode("ascii")
    request = urllib.request.Request(
        YOOKASSA_API,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Basic {token}",
            "Idempotence-Key": str(uuid.uuid4()),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, context=context, timeout=15) as response:
        return json.load(response)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self._send_json({"ok": True}, status=204)

    def do_POST(self) -> None:
        try:
            content_length = int(self.headers.get("content-length", 0))
            payload = json.loads(self.rfile.read(content_length) or b"{}")
            self._send_json(create_checkout(payload))
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=400)

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if status != 204:
            self.wfile.write(body)


def main() -> None:
    import sys

    payload = json.loads(sys.stdin.read() or "{}")
    print(json.dumps(create_checkout(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
