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


def test_algorithm_version_is_sun_sign():
    assert ALGORITHM_VERSION == "astrology-sun-sign-v1"


def test_element_scores_weighted_is_informative():
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


def test_auto_uses_sun_sign_element():
    for sun_sign, expected in [
        ("Aries", "fire"), ("Leo", "fire"), ("Sagittarius", "fire"),
        ("Taurus", "earth"), ("Virgo", "earth"), ("Capricorn", "earth"),
        ("Gemini", "air"), ("Libra", "air"), ("Aquarius", "air"),
        ("Cancer", "water"), ("Scorpio", "water"), ("Pisces", "water"),
    ]:
        r = assign_theme({"sun": sign(sun_sign)}, requested_theme="auto", book_id="b1")
        assert r["resolved_theme"] == expected
        assert r["resolution_reason"] == "sun_sign"
        assert r["dominant_element"] == expected


def test_sun_sign_wins_over_other_placements():
    # Sun in Aries (fire) even though everything else is water.
    chart = {
        "sun": sign("Aries"),
        "moon": sign("Cancer"), "mercury": sign("Scorpio"),
        "venus": sign("Pisces"), "mars": sign("Cancer"),
    }
    r = assign_theme(chart, requested_theme="auto", book_id="b1")
    assert r["resolved_theme"] == "fire"
    assert r["resolution_reason"] == "sun_sign"


def test_user_choice_overrides_sun_sign():
    chart = {"sun": sign("Libra")}  # air
    r = assign_theme(chart, requested_theme="fire", book_id="b1")
    assert r["resolved_theme"] == "fire"
    assert r["resolution_reason"] == "user_choice"
    assert r["dominant_element"] == "air"  # reported Sun element, but user wins


def test_no_sun_sign_hash_fallback_is_deterministic():
    chart = {"moon": sign("Cancer")}  # no Sun
    r1 = assign_theme(chart, requested_theme="auto", book_id="seed-42")
    r2 = assign_theme(chart, requested_theme="auto", book_id="seed-42")
    assert r1["resolved_theme"] in THEMES
    assert r1["resolution_reason"] == "hash_fallback"
    assert "no_sun_sign" in r1["warnings"]
    assert r1["resolved_theme"] == r2["resolved_theme"]


def test_hash_fallback_when_empty():
    r = assign_theme({}, requested_theme="auto", book_id="seed-42")
    assert r["resolved_theme"] in THEMES
    assert r["resolution_reason"] == "hash_fallback"


def test_ascendant_ignored_when_angles_not_allowed():
    chart = {"sun": sign("Libra"), "asc": sign("Aries")}
    with_angles = compute_element_scores(chart, angles_allowed=True)
    without = compute_element_scores(chart, angles_allowed=False)
    assert with_angles["fire"] == 2 and without["fire"] == 0
    assert without["air"] == 3


def test_ambiguous_moon_not_counted_in_scores():
    chart = {"sun": sign("Aries"), "moon": sign("Cancer")}
    scores = compute_element_scores(chart, angles_allowed=False, moon_reliable=False)
    assert scores["water"] == 0 and scores["fire"] == 3


def test_low_reliability_placement_excluded_from_scores():
    chart = {"sun": {"sign": "Libra", "reliability": "low"}, "moon": sign("Gemini")}
    scores = compute_element_scores(chart, angles_allowed=False)
    assert scores["air"] == 3  # only the moon counts


def test_invalid_requested_theme_falls_back_to_auto():
    chart = {"sun": sign("Libra")}
    r = assign_theme(chart, requested_theme="purple", book_id="b1")
    assert r["resolved_theme"] == "air"
    assert r["resolution_reason"] == "sun_sign"
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
    assert theme_tokens("cosmic_night") == THEME_TOKENS["water"]


def test_deterministic_same_input():
    chart = {"sun": sign("Scorpio")}
    a = assign_theme(chart, requested_theme="auto", book_id="x")
    b = assign_theme(chart, requested_theme="auto", book_id="x")
    assert a == b
