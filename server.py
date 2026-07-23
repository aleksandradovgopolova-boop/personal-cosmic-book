#!/usr/bin/env python3
"""Standalone HTTP server for self-hosting (Russian VPS / Timeweb Cloud / Docker).

On Vercel the `api/*.py` functions and the Next rewrite serve everything; this
server is the host-agnostic alternative. It serves the static site from
``public/`` (landing at ``/``) and the JSON API endpoints from one process:

    POST /api/chart     -> natal chart (kerykeion + numerology + saju)
    POST /api/book      -> personal 10-section book (two-stage DeepSeek + theme)
    POST /api/checkout  -> checkout (demo, or YooKassa when configured)

Run: ``python server.py`` (PORT / HOST via env, default 0.0.0.0:8000).
"""
from __future__ import annotations

import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from api.book import book_from_payload
from api.chart import chart_from_payload
from api.checkout import create_checkout

PUBLIC_DIR = (Path(__file__).parent / "public").resolve()

API_ROUTES = {
    "/api/chart": chart_from_payload,
    "/api/book": book_from_payload,
    "/api/checkout": create_checkout,
}

_TEXT_TYPES = ("text/", "application/json", "application/xml", "image/svg+xml", "application/javascript")


class Handler(BaseHTTPRequestHandler):
    server_version = "PersonalCosmicBook/1.0"
    protocol_version = "HTTP/1.1"

    def do_OPTIONS(self) -> None:
        self._cors(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self) -> None:
        route = self.path.split("?", 1)[0]
        fn = API_ROUTES.get(route)
        if fn is None:
            return self._json({"error": "not found"}, 404)
        try:
            length = int(self.headers.get("content-length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            self._json(fn(payload), 200)
        except Exception as exc:  # noqa: BLE001 - report, don't crash the server
            self._json({"error": str(exc)}, 400)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", ""):
            return self._file(PUBLIC_DIR / "landing.html")
        target = (PUBLIC_DIR / path.lstrip("/")).resolve()
        if not str(target).startswith(str(PUBLIC_DIR)):
            return self._json({"error": "forbidden"}, 403)
        if target.is_file():
            return self._file(target)
        return self._json({"error": "not found"}, 404)

    # ── helpers ──
    def _file(self, path: Path) -> None:
        if not path.is_file():
            return self._json({"error": "not found"}, 404)
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if any(ctype.startswith(t) for t in _TEXT_TYPES):
            ctype += "; charset=utf-8"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _cors(self, status: int) -> None:
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, obj, status: int) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._cors(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if status != 204:
            self.wfile.write(body)

    def log_message(self, *args) -> None:  # keep stdout clean
        return


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Personal Cosmic Book server on http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
