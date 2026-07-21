from api.theme import (
    ALGORITHM_VERSION,
    LEGACY_THEME_ALIASES,
    THEMES,
    THEME_TOKENS,
    assign_theme,
    compute_element_scores,
    normalize_theme,
    theme_tokens,
)


def sign(s):
    return {"sign": s}


def test_element_scores_weighted():
    chart = {
        "sun": sign("Libra"),      # air +3
        "moon": sign("Aquarius"),  # air +3
        "mercury": sign("Gemini"), # air +2
        "venus": sign("Taurus"),   # earth +2
        "mars": sign("Aries"),     # fire +2
        "jupiter": sign("Cancer"), # water +1
    }
    scores = compute_element_scores(chart, angles_allowed=False)
    assert scores == {"air": 8, "earth": 2, "fire": 2, "water": 1}


def test_dominant_exact_win():
    chart = {"sun": sign("Libra"), "moon": sign("Gemini"), "venus": sign("Aquarius")}
    r = assign_theme(chart, requested_theme="auto", book_id="b1")
    assert r["resolved_theme"] == "air"
    assert r["resolution_reason"] == "dominant_element"
    assert r["dominant_element"] == "air"
    assert r["algorithm_version"] == ALGORITHM_VERSION


def test_user_choice_overrides_scores():
    chart = {"sun": sign("Libra"), "moon": sign("Gemini")}  # air-heavy
    r = assign_theme(chart, requested_theme="fire", book_id="b1")
    assert r["resolved_theme"] == "fire"
    assert r["resolution_reason"] == "user_choice"


def test_tie_broken_by_sun():
    chart = {"sun": sign("Aries"), "moon": sign("Cancer")}  # fire 3 vs water 3
    r = assign_theme(chart, requested_theme="auto", book_id="b1")
    assert r["resolved_theme"] == "fire"
    assert r["tie_breaker"] == "sun"
    assert r["resolution_reason"] == "dominant_element"


def test_tie_broken_by_moon_when_sun_not_leader():
    chart = {
        "sun": sign("Aries"),    # fire +3 (not a leader)
        "moon": sign("Cancer"),  # water +3
        "venus": sign("Taurus"), # earth +2
        "mars": sign("Virgo"),   # earth +2  -> earth 4
        "jupiter": sign("Pisces"),  # water +1 -> water 4
    }
    r = assign_theme(chart, requested_theme="auto", book_id="b1")
    assert r["element_scores"]["earth"] == 4 and r["element_scores"]["water"] == 4
    assert r["resolved_theme"] == "water"
    assert r["tie_breaker"] == "moon"


def test_tie_broken_by_hash_is_deterministic():
    chart = {
        "sun": sign("Aries"),     # fire +3 (not leader)
        "mercury": sign("Taurus"),# earth +2
        "venus": sign("Virgo"),   # earth +2 -> earth 4
        "mars": sign("Scorpio"),  # water +2
        "jupiter": sign("Pisces"),# water +1
        "saturn": sign("Cancer"), # water +1 -> water 4
    }
    r1 = assign_theme(chart, requested_theme="auto", book_id="stable-xyz", moon_reliable=False)
    r2 = assign_theme(chart, requested_theme="auto", book_id="stable-xyz", moon_reliable=False)
    assert r1["resolved_theme"] in ("earth", "water")
    assert r1["tie_breaker"] == "hash"
    assert r1["resolved_theme"] == r2["resolved_theme"]


def test_ascendant_ignored_when_angles_not_allowed():
    chart = {"sun": sign("Libra"), "asc": sign("Aries")}
    with_angles = compute_element_scores(chart, angles_allowed=True)
    without = compute_element_scores(chart, angles_allowed=False)
    assert with_angles["fire"] == 2 and without["fire"] == 0
    assert without["air"] == 3


def test_ambiguous_moon_not_counted():
    chart = {"sun": sign("Aries"), "moon": sign("Cancer")}
    scores = compute_element_scores(chart, angles_allowed=False, moon_reliable=False)
    assert scores["water"] == 0 and scores["fire"] == 3


def test_low_reliability_placement_excluded():
    chart = {"sun": {"sign": "Libra", "reliability": "low"}, "moon": sign("Gemini")}
    scores = compute_element_scores(chart, angles_allowed=False)
    assert scores["air"] == 3  # only the moon counts


def test_hash_fallback_when_no_data():
    r = assign_theme({}, requested_theme="auto", book_id="seed-42")
    assert r["resolved_theme"] in THEMES
    assert r["resolution_reason"] == "hash_fallback"
    assert "insufficient_astrology_data" in r["warnings"]
    # deterministic
    assert assign_theme({}, requested_theme="auto", book_id="seed-42")["resolved_theme"] == r["resolved_theme"]


def test_invalid_requested_theme_falls_back_to_auto():
    chart = {"sun": sign("Libra"), "moon": sign("Gemini")}
    r = assign_theme(chart, requested_theme="purple", book_id="b1")
    assert r["resolved_theme"] == "air"
    assert any("invalid requested_theme" in w for w in r["warnings"])


def test_legacy_theme_migration():
    assert normalize_theme("cosmic_night") == "water"
    assert normalize_theme("solar_dawn") == "fire"
    assert normalize_theme("lunar_mist") == "air"
    assert normalize_theme("water") == "water"
    assert normalize_theme("unknown") is None
    assert normalize_theme(None) is None
    assert set(LEGACY_THEME_ALIASES.values()) <= set(THEMES)


def test_theme_tokens_complete():
    assert set(THEME_TOKENS.keys()) == set(THEMES)
    for name in THEMES:
        tok = theme_tokens(name)
        for key in ("cover_background", "content_background", "primary", "text", "pattern", "symbol"):
            assert key in tok
    # legacy id resolves through tokens
    assert theme_tokens("cosmic_night") == THEME_TOKENS["water"]
