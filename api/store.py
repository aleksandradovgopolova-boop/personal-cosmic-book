"""Optional persistence to Supabase (PostgREST).

Writes are best-effort and fully gated: without SUPABASE_URL +
SUPABASE_SERVICE_ROLE_KEY every function is a no-op, so the product works
without a database. The service role is used server-side only and bypasses
RLS; the tables have no public policies (see migration 002).
"""
from __future__ import annotations

import json
import os
import ssl
import urllib.request
from typing import Any, Dict, Optional


def _config() -> Optional[tuple]:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return url.rstrip("/"), key
    return None


def is_configured() -> bool:
    return _config() is not None


def _post(table: str, row: Dict[str, Any], *, on_conflict: Optional[str] = None) -> Optional[int]:
    cfg = _config()
    if not cfg:
        return None
    base_url, key = cfg
    endpoint = f"{base_url}/rest/v1/{table}"
    if on_conflict:
        endpoint += f"?on_conflict={on_conflict}"
    prefer = "resolution=merge-duplicates,return=minimal" if on_conflict else "return=minimal"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(row, ensure_ascii=False).encode("utf-8"),
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": prefer,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, context=ssl.create_default_context(), timeout=10) as response:
            return getattr(response, "status", 200)
    except Exception:
        return None


def save_order(*, email: str, product: str, amount: int, status: str, input_data: Optional[Dict[str, Any]] = None) -> Optional[int]:
    return _post("generation_orders", {
        "email": email,
        "product": product,
        "amount": amount,
        "status": status,
        "input_data": input_data or {},
    })


def save_book(book: Dict[str, Any]) -> Optional[int]:
    if not book.get("book_id"):
        return None
    return _post(
        "generation_books",
        {
            "book_id": book.get("book_id"),
            "subject_name": (book.get("cover") or {}).get("name"),
            "resolved_theme": book.get("resolved_theme"),
            "generated_with": book.get("generated_with"),
            "sections": book.get("sections"),
        },
        on_conflict="book_id",
    )
