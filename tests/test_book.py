from api.book import DISCLAIMER, SECTION_IDS, build_book
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
