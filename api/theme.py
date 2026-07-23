"""Deterministic element -> visual theme assignment (astrology-four-elements-v1).

This module is intentionally independent of the LLM. Given a computed natal
chart it returns a stable visual theme. It must never be fed the book text,
Saju, numerology or the destiny matrix (see input-data-contract-v3.md).
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

ALGORITHM_VERSION = "astrology-sun-sign-v1"

THEMES = ("earth", "water", "air", "fire")

# requested_theme accepts THEMES + "auto"; resolved_theme accepts THEMES only.
VALID_REQUESTED = set(THEMES) | {"auto"}

# Temporary migration aliases for legacy stored theme IDs.
LEGACY_THEME_ALIASES = {
    "cosmic_night": "water",
    "solar_dawn": "fire",
    "lunar_mist": "air",
}

# Sign -> element (western four elements). Keys are canonical lowercase English.
ELEMENT_BY_SIGN = {
    "aries": "fire", "leo": "fire", "sagittarius": "fire",
    "taurus": "earth", "virgo": "earth", "capricorn": "earth",
    "gemini": "air", "libra": "air", "aquarius": "air",
    "cancer": "water", "scorpio": "water", "pisces": "water",
}

# Weights v1. Ascendant only counts when angles are allowed.
OBJECT_WEIGHTS = {
    "sun": 3,
    "moon": 3,
    "asc": 2,
    "mercury": 2,
    "venus": 2,
    "mars": 2,
    "jupiter": 1,
    "saturn": 1,
}

_SIGN_ALIASES = {
    "ari": "aries", "aries": "aries", "овен": "aries",
    "tau": "taurus", "taurus": "taurus", "телец": "taurus",
    "gem": "gemini", "gemini": "gemini", "близнецы": "gemini",
    "can": "cancer", "cnc": "cancer", "cancer": "cancer", "рак": "cancer",
    "leo": "leo", "лев": "leo",
    "vir": "virgo", "virgo": "virgo", "дева": "virgo",
    "lib": "libra", "libra": "libra", "весы": "libra",
    "sco": "scorpio", "scorpio": "scorpio", "скорпион": "scorpio",
    "sag": "sagittarius", "sgr": "sagittarius", "sagittarius": "sagittarius", "стрелец": "sagittarius",
    "cap": "capricorn", "capricorn": "capricorn", "козерог": "capricorn",
    "aqu": "aquarius", "aquarius": "aquarius", "водолей": "aquarius",
    "pis": "pisces", "psc": "pisces", "pisces": "pisces", "рыбы": "pisces",
}


def normalize_theme(value: Optional[str]) -> Optional[str]:
    """Normalize a stored/legacy theme id to a valid theme, or None."""
    if not value:
        return None
    key = str(value).strip().lower()
    key = LEGACY_THEME_ALIASES.get(key, key)
    return key if key in THEMES else None


def _sign_element(sign: Any) -> Optional[str]:
    if not sign:
        return None
    canonical = _SIGN_ALIASES.get(str(sign).strip().lower())
    return ELEMENT_BY_SIGN.get(canonical) if canonical else None


def _stable_hash_choice(seed: str, candidates: List[str]) -> str:
    ordered = [t for t in THEMES if t in candidates]  # deterministic candidate order
    digest = hashlib.sha256(str(seed).encode("utf-8")).hexdigest()
    return ordered[int(digest, 16) % len(ordered)]


def compute_element_scores(
    chart: Dict[str, Any],
    *,
    angles_allowed: Optional[bool] = None,
    moon_reliable: bool = True,
) -> Dict[str, int]:
    """Score the four elements from weighted chart placements.

    - Ascendant ("asc") is counted only when angles are allowed.
    - The Moon is skipped when it is not reliable (e.g. unknown birth time and
      an ambiguous sign) — we never guess.
    """
    if angles_allowed is None:
        angles_allowed = isinstance(chart.get("asc"), dict) and bool(
            _sign_element((chart.get("asc") or {}).get("sign"))
        )

    scores = {t: 0 for t in THEMES}
    for obj, weight in OBJECT_WEIGHTS.items():
        if obj == "asc" and not angles_allowed:
            continue
        if obj == "moon" and not moon_reliable:
            continue
        node = chart.get(obj)
        if not isinstance(node, dict):
            continue
        if str(node.get("reliability", "")).lower() in ("low", "excluded"):
            continue
        element = _sign_element(node.get("sign"))
        if element:
            scores[element] += weight
    return scores


def assign_theme(
    chart: Optional[Dict[str, Any]] = None,
    *,
    requested_theme: str = "auto",
    book_id: str = "",
    angles_allowed: Optional[bool] = None,
    moon_reliable: bool = True,
) -> Dict[str, Any]:
    """Return a deterministic visual_assignment block.

    Auto mode resolves the theme strictly from the Sun-sign element
    (astrology-sun-sign-v1). ``element_scores`` is still reported as an
    informative weighted profile but does not drive the auto decision.
    """
    chart = chart or {}
    warnings: List[str] = []
    requested = str(requested_theme or "auto").strip().lower()
    if requested not in VALID_REQUESTED:
        warnings.append(f"invalid requested_theme '{requested_theme}', treated as auto")
        requested = "auto"

    scores = compute_element_scores(chart, angles_allowed=angles_allowed, moon_reliable=moon_reliable)
    sun_element = _sign_element((chart.get("sun") or {}).get("sign")) if isinstance(chart.get("sun"), dict) else None

    result = {
        "algorithm_version": ALGORITHM_VERSION,
        "element_scores": scores,
        "sun_element": sun_element,
        "dominant_element": None,
        "resolved_theme": None,
        "resolution_reason": None,
        "tie_breaker": None,
        "warnings": warnings,
    }

    # 1. Explicit user choice always wins.
    if requested in THEMES:
        result["resolved_theme"] = requested
        result["resolution_reason"] = "user_choice"
        result["dominant_element"] = sun_element
        return result

    # 2. Auto: theme = element of the Sun sign.
    if sun_element:
        result["dominant_element"] = sun_element
        result["resolved_theme"] = sun_element
        result["resolution_reason"] = "sun_sign"
        return result

    # 3. No Sun sign available -> stable hash over the four themes.
    warnings.append("no_sun_sign")
    result["resolved_theme"] = _stable_hash_choice(book_id, list(THEMES))
    result["resolution_reason"] = "hash_fallback"
    return result


# ── Immutable design tokens (design-system-elements-v2, dark edition) ──
# One premium dark layout, four elemental palettes. ``content_background`` is
# the page background (dark); ``cover_background`` is the radial-glow centre of
# the cover. ``surface``/``surface2`` build card gradients, ``accent``/``accent2``
# are the tertiary/quaternary accents, ``dim`` is muted body text and ``line``
# is the hairline colour. Legacy keys (cover_text, primary, secondary, text,
# metal, pattern, symbol) are preserved for the renderer and tests.
THEME_TOKENS = {
    "earth": {
        "content_background": "#0A0B07", "cover_background": "#1A1C10", "cover_text": "#F1ECE0",
        "surface": "#181A12", "surface2": "#20231A",
        "primary": "#CDB079", "secondary": "#B07C52", "accent": "#8FA06A", "accent2": "#C6924F",
        "text": "#F1ECE0", "dim": "rgba(241,236,224,0.70)", "line": "rgba(205,176,121,0.18)",
        "metal": "#CDB079", "pattern": "strata", "symbol": "earth",
    },
    "water": {
        "content_background": "#080B0F", "cover_background": "#0D1624", "cover_text": "#EAE6F0",
        "surface": "#141820", "surface2": "#1C2230",
        "primary": "#C8D4E8", "secondary": "#7BA7D4", "accent": "#6ECFCB", "accent2": "#E8C87A",
        "text": "#EAE6F0", "dim": "rgba(234,230,240,0.70)", "line": "rgba(200,212,232,0.16)",
        "metal": "#7BA7D4", "pattern": "ripples", "symbol": "water",
    },
    "air": {
        "content_background": "#090A0E", "cover_background": "#121522", "cover_text": "#EEF0F4",
        "surface": "#14161F", "surface2": "#1B1E2A",
        "primary": "#CBD3E6", "secondary": "#9AB8D4", "accent": "#E6E0D2", "accent2": "#B4A9E0",
        "text": "#EEF0F4", "dim": "rgba(238,240,244,0.70)", "line": "rgba(154,184,212,0.16)",
        "metal": "#9AB8D4", "pattern": "currents", "symbol": "air",
    },
    "fire": {
        "content_background": "#0D0908", "cover_background": "#24100C", "cover_text": "#F2E9E2",
        "surface": "#1A1210", "surface2": "#231816",
        "primary": "#E0A85A", "secondary": "#C85A4A", "accent": "#C4876A", "accent2": "#D98A5A",
        "text": "#F2E9E2", "dim": "rgba(242,233,226,0.70)", "line": "rgba(224,168,90,0.18)",
        "metal": "#E0A85A", "pattern": "rays", "symbol": "fire",
    },
}

THEME_LABELS = {
    "earth": "Земля · Корни",
    "water": "Вода · Глубина",
    "air": "Воздух · Дыхание",
    "fire": "Огонь · Искра",
}


def theme_tokens(resolved_theme: str) -> Dict[str, Any]:
    """Return the immutable token set for a resolved theme (safe fallback: water)."""
    return THEME_TOKENS.get(normalize_theme(resolved_theme) or "water", THEME_TOKENS["water"])
