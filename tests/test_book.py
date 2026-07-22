import api.book as bk
from api.book import DISCLAIMER, SECTION_IDS, SECTIONS, build_book, generate_book
from api.theme import THEMES

EXPECTED_IDS = [
    "01_main_theme", "02_inner_world", "03_strengths", "04_inner_tensions",
    "05_love", "06_realization", "07_outer_expression", "08_life_patterns",
    "09_personal_formula", "10_next_chapter",
]

CHART = {
    "subject": {"name": "Аня", "date": "1996-06-20", "time": "14:30", "city": "Москва"},
    "input_hash": "abc123def456",
    "numerology": {"life_path": 6, "name_number": 3},
    "saju": {"day_pillar": {"stem": "Bing Fire", "branch": "Yin Tiger"}},
    "astrology_available": True,
    "sun": {"sign": "Gemini"}, "moon": {"sign": "Libra"}, "asc": {"sign": "Aquarius"},
}


def test_section_ids_constant():
    assert SECTION_IDS == EXPECTED_IDS


def test_book_has_exactly_ten_sections_in_order():
    book = build_book(CHART, requested_theme="auto", book_id="abc123")
    assert [s["id"] for s in book["sections"]] == EXPECTED_IDS
    assert len(book["sections"]) == 10


def test_every_section_has_title_and_blocks():
    book = build_book(CHART, requested_theme="auto", book_id="abc123")
    for section in book["sections"]:
        assert section["title"]
        assert section["blocks"] and all(b["paragraphs"] for b in section["blocks"])


def test_resolved_theme_is_valid_enum():
    book = build_book(CHART, requested_theme="auto", book_id="abc123")
    assert book["resolved_theme"] in THEMES
    assert book["theme_tokens"]["symbol"] == book["element_symbol"]


def test_disclaimer_present():
    book = build_book(CHART, requested_theme="auto", book_id="abc123")
    assert book["disclaimer"] == DISCLAIMER
    assert "развлекательный" in book["disclaimer"]


def test_user_theme_override():
    book = build_book(CHART, requested_theme="earth", book_id="abc123")
    assert book["resolved_theme"] == "earth"
    assert book["visual_assignment"]["resolution_reason"] == "user_choice"


def test_template_generation_marker():
    book = build_book(CHART, requested_theme="auto", book_id="abc123")
    assert book["generated_with"] == "template"


def test_deterministic_same_input():
    a = build_book(CHART, requested_theme="auto", book_id="abc123")
    b = build_book(CHART, requested_theme="auto", book_id="abc123")
    assert a["resolved_theme"] == b["resolved_theme"]
    assert a["signature_seed"] == b["signature_seed"]


def test_auto_theme_matches_sun_sign():
    # Sun in Gemini (air) via the real placement.
    book = build_book(CHART, requested_theme="auto", book_id="abc123")
    assert book["resolved_theme"] == "air"
    assert book["visual_assignment"]["resolution_reason"] == "sun_sign"


def test_theme_from_date_without_astrology():
    chart = {
        "subject": {"name": "X", "date": "1996-06-20", "city": "Москва"},
        "input_hash": "z", "numerology": {"life_path": 6},
        "saju": {"day_pillar": {"stem": "Bing Fire"}}, "astrology_available": False,
    }
    book = build_book(chart, requested_theme="auto", book_id="z")
    assert book["resolved_theme"] == "air"  # 1996-06-20 -> Gemini -> air
    assert book["visual_assignment"]["resolution_reason"] == "sun_sign"


def test_two_stage_generation_uses_patterns(monkeypatch):
    fake_patterns = {
        "patterns": [{"id": f"p{i}", "thesis": f"тезис {i}"} for i in range(1, 5)],
        "synthesis": {"central_tension": "..."},
    }
    fake_sections = {"sections": [
        {"id": s["id"], "title": s["title"], "blocks": [{"paragraphs": [f"Абзац про {s['id']}"]}]}
        for s in SECTIONS
    ]}

    def fake_chat(system, user, **kwargs):
        return fake_patterns if "аналитический" in system else fake_sections

    monkeypatch.setattr(bk, "_deepseek_chat", fake_chat)
    book = generate_book(CHART, requested_theme="auto", book_id="abc123")
    assert book["generated_with"] == "deepseek-2stage"
    assert [s["id"] for s in book["sections"]] == EXPECTED_IDS
    assert "patterns" in book and len(book["patterns"]["patterns"]) == 4
    assert book["sections"][0]["blocks"][0]["paragraphs"][0].startswith("Абзац про")


def test_two_stage_falls_back_to_template_when_stage2_fails(monkeypatch):
    monkeypatch.setattr(bk, "_deepseek_chat", lambda system, user, **kw: None)
    book = generate_book(CHART, requested_theme="auto", book_id="abc123")
    assert book["generated_with"] == "template"
    assert len(book["sections"]) == 10


def test_stage2_rejects_too_few_patterns(monkeypatch):
    # Stage 2 returns only 2 patterns -> invalid -> template fallback.
    def fake_chat(system, user, **kwargs):
        if "аналитический" in system:
            return {"patterns": [{"id": "p1", "thesis": "t"}, {"id": "p2", "thesis": "t"}]}
        return {"sections": []}
    monkeypatch.setattr(bk, "_deepseek_chat", fake_chat)
    book = generate_book(CHART, requested_theme="auto", book_id="abc123")
    assert book["generated_with"] == "template"
