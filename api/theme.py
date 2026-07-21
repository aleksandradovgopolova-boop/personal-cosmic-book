"""Deterministic element -> visual theme assignment (astrology-four-elements-v1).

This module is intentionally independent of the LLM. Given a computed natal
chart it returns a stable visual theme. It must never be fed the book text,
Saju, numerology or the destiny matrix (see input-data-contract-v3.md).
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

ALGORITHM_VERSION = "astrology-four-elements-v1"

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
    """Return a deterministic visual_assignment block (see input-data-contract-v3)."""
    chart = chart or {}
    warnings: List[str] = []
    requested = str(requested_theme or "auto").strip().lower()
    if requested not in VALID_REQUESTED:
        warnings.append(f"invalid requested_theme '{requested_theme}', treated as auto")
        requested = "auto"

    scores = compute_element_scores(chart, angles_allowed=angles_allowed, moon_reliable=moon_reliable)

    result = {
        "algorithm_version": ALGORITHM_VERSION,
        "element_scores": scores,
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
        if any(scores.values()):
            result["dominant_element"] = _dominant(scores)
        return result

    # 2. Auto: not enough astrological data -> stable hash over the four themes.
    total = sum(scores.values())
    if total == 0:
        warnings.append("insufficient_astrology_data")
        theme = _stable_hash_choice(book_id, list(THEMES))
        result["resolved_theme"] = theme
        result["resolution_reason"] = "hash_fallback"
        return result

    # 3. Auto: dominant element, with deterministic tie-breaking.
    leaders = _leaders(scores)
    result["dominant_element"] = leaders[0] if len(leaders) == 1 else None
    if len(leaders) == 1:
        result["resolved_theme"] = leaders[0]
        result["resolution_reason"] = "dominant_element"
        return result

    # Tie-break: Sun element -> reliable Moon element -> stable hash, among leaders.
    sun_el = _sign_element((chart.get("sun") or {}).get("sign")) if isinstance(chart.get("sun"), dict) else None
    moon_el = _sign_element((chart.get("moon") or {}).get("sign")) if (moon_reliable and isinstance(chart.get("moon"), dict)) else None

    if sun_el in leaders:
        theme, tb = sun_el, "sun"
    elif moon_el in leaders:
        theme, tb = moon_el, "moon"
    else:
        theme, tb = _stable_hash_choice(book_id, leaders), "hash"

    result["dominant_element"] = theme
    result["resolved_theme"] = theme
    result["resolution_reason"] = "dominant_element"
    result["tie_breaker"] = tb
    return result


def _dominant(scores: Dict[str, int]) -> Optional[str]:
    leaders = _leaders(scores)
    return leaders[0] if len(leaders) == 1 else None


def _leaders(scores: Dict[str, int]) -> List[str]:
    top = max(scores.values())
    if top == 0:
        return []
    return [t for t in THEMES if scores[t] == top]


# ── Immutable design tokens (design-system-elements-v2.md) ──
THEME_TOKENS = {
    "earth": {
        "cover_background": "#293029", "cover_text": "#F7F0E3", "content_background": "#F7F1E7",
        "primary": "#66704F", "secondary": "#A66A4A", "text": "#2F2B26",
        "metal": "#B9975B", "pattern": "strata", "symbol": "earth",
    },
    "water": {
        "cover_background": "#102A3A", "cover_text": "#F2F7F8", "content_background": "#F4F8FA",
        "primary": "#3E748D", "secondary": "#7B9FAE", "text": "#24313A",
        "metal": "#AABBC4", "pattern": "ripples", "symbol": "water",
    },
    "air": {
        "cover_background": "#DDE8ED", "cover_text": "#263741", "content_background": "#FAFCFD",
        "primary": "#507A8B", "secondary": "#8AA7B3", "text": "#27343B",
        "metal": "#9EADB4", "pattern": "currents", "symbol": "air",
    },
    "fire": {
        "cover_background": "#3A201D", "cover_text": "#FFF4E8", "content_background": "#FFF7EF",
        "primary": "#A94E37", "secondary": "#C8873F", "text": "#342622",
        "metal": "#C19B61", "pattern": "rays", "symbol": "fire",
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
