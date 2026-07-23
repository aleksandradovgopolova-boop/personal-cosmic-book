import json

import api.store as store


class _Resp:
    status = 201

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _use_supabase(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://proj.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "svc-key")


def test_noop_without_config(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    assert store.is_configured() is False
    assert store.save_order(email="a@b.ru", product="pcb_basic", amount=990, status="demo") is None
    assert store.save_book({"book_id": "x"}) is None


def test_save_order_posts_row(monkeypatch):
    _use_supabase(monkeypatch)
    captured = {}

    def fake_urlopen(req, *a, **kw):
        captured["url"] = req.full_url
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["headers"] = {k.lower(): v for k, v in req.header_items()}
        return _Resp()

    monkeypatch.setattr(store.urllib.request, "urlopen", fake_urlopen)
    rc = store.save_order(email="a@b.ru", product="pcb_basic", amount=990, status="demo", input_data={"k": 1})
    assert rc == 201
    assert captured["url"].endswith("/rest/v1/generation_orders")
    assert captured["body"] == {"email": "a@b.ru", "product": "pcb_basic", "amount": 990, "status": "demo", "input_data": {"k": 1}}
    assert captured["headers"]["apikey"] == "svc-key"
    assert captured["headers"]["authorization"] == "Bearer svc-key"


def test_save_book_upserts_by_book_id(monkeypatch):
    _use_supabase(monkeypatch)
    captured = {}

    def fake_urlopen(req, *a, **kw):
        captured["url"] = req.full_url
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["prefer"] = {k.lower(): v for k, v in req.header_items()}.get("prefer", "")
        return _Resp()

    monkeypatch.setattr(store.urllib.request, "urlopen", fake_urlopen)
    book = {
        "book_id": "bid1", "cover": {"name": "Аня"}, "resolved_theme": "air",
        "generated_with": "template", "sections": [{"id": "01_main_theme"}],
    }
    store.save_book(book)
    assert "on_conflict=book_id" in captured["url"]
    assert captured["body"]["book_id"] == "bid1"
    assert captured["body"]["subject_name"] == "Аня"
    assert captured["body"]["resolved_theme"] == "air"
    assert "merge-duplicates" in captured["prefer"]


def test_save_book_without_id_is_noop(monkeypatch):
    _use_supabase(monkeypatch)
    assert store.save_book({}) is None


def test_post_swallows_errors(monkeypatch):
    _use_supabase(monkeypatch)

    def boom(req, *a, **kw):
        raise OSError("network down")

    monkeypatch.setattr(store.urllib.request, "urlopen", boom)
    assert store.save_order(email="a@b.ru", product="pcb_basic", amount=990, status="demo") is None
