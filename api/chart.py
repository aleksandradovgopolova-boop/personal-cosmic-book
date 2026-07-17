from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, Iterable, Optional


PLANETS = (
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "mean_node",
    "true_node",
    "chiron",
)

CITY_FALLBACKS = {
    ("moscow", "ru"): {"lat": 55.7558, "lng": 37.6173, "tz": "Europe/Moscow"},
    ("москва", "ru"): {"lat": 55.7558, "lng": 37.6173, "tz": "Europe/Moscow"},
    ("saint petersburg", "ru"): {"lat": 59.9311, "lng": 30.3609, "tz": "Europe/Moscow"},
    ("санкт-петербург", "ru"): {"lat": 59.9311, "lng": 30.3609, "tz": "Europe/Moscow"},
    ("new york", "us"): {"lat": 40.7128, "lng": -74.006, "tz": "America/New_York"},
    ("london", "gb"): {"lat": 51.5072, "lng": -0.1276, "tz": "Europe/London"},
}

STEMS = (
    "Jia Wood",
    "Yi Wood",
    "Bing Fire",
    "Ding Fire",
    "Wu Earth",
    "Ji Earth",
    "Geng Metal",
    "Xin Metal",
    "Ren Water",
    "Gui Water",
)
BRANCHES = (
    "Zi Rat",
    "Chou Ox",
    "Yin Tiger",
    "Mao Rabbit",
    "Chen Dragon",
    "Si Snake",
    "Wu Horse",
    "Wei Goat",
    "Shen Monkey",
    "You Rooster",
    "Xu Dog",
    "Hai Pig",
)


def get_chart(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    city: str,
    country: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    timezone: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a normalized chart JSON for the product pipeline."""

    subject = _build_subject(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city,
        country=country,
        lat=lat,
        lng=lng,
        timezone=timezone,
    )

    bodies = {planet: _body(subject, planet) for planet in PLANETS if _has(subject, planet)}
    houses = {
        "asc": _angle(subject, "first_house"),
        "mc": _angle(subject, "tenth_house"),
    }

    return {
        "subject": {
            "name": name,
            "date": f"{year:04d}-{month:02d}-{day:02d}",
            "time": f"{hour:02d}:{minute:02d}",
            "city": city,
            "country": country,
        },
        "input_hash": _input_hash(year, month, day, hour, minute, city, country),
        **bodies,
        **houses,
        "aspects": _aspects(subject),
        "numerology": _numerology(year, month, day, name),
        "saju": _saju(year, month, day, hour),
    }


def chart_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    birth_date = payload.get("date") or payload.get("birthDate")
    birth_time = payload.get("time") or payload.get("birthTime") or "12:00"
    if not birth_date:
        raise ValueError("date is required")

    year, month, day = [int(part) for part in birth_date.split("-")]
    hour, minute = [int(part) for part in birth_time.split(":")[:2]]
    city = str(payload.get("city") or "")
    country = str(payload.get("country") or payload.get("nation") or "")
    fallback = CITY_FALLBACKS.get((city.strip().lower(), country.strip().lower()), {})

    return get_chart(
        name=str(payload.get("name") or "Subject"),
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city,
        country=country,
        lat=_float_or_none(payload.get("lat", fallback.get("lat"))),
        lng=_float_or_none(payload.get("lng", payload.get("lon", fallback.get("lng")))),
        timezone=payload.get("timezone") or payload.get("tz") or fallback.get("tz"),
    )


def _build_subject(**kwargs: Any) -> Any:
    try:
        from kerykeion import AstrologicalSubject
    except ImportError as exc:
        raise RuntimeError("Install kerykeion with: python3 -m pip install -r requirements.txt") from exc

    base_args = (
        kwargs["name"],
        kwargs["year"],
        kwargs["month"],
        kwargs["day"],
        kwargs["hour"],
        kwargs["minute"],
        kwargs["city"],
        kwargs["country"],
    )

    if kwargs.get("lat") is not None and kwargs.get("lng") is not None and kwargs.get("timezone"):
        attempts = (
            {
                "lat": kwargs["lat"],
                "lng": kwargs["lng"],
                "tz_str": kwargs["timezone"],
                "online": False,
            },
            {
                "latitude": kwargs["lat"],
                "longitude": kwargs["lng"],
                "timezone": kwargs["timezone"],
                "online": False,
            },
        )
        for extra in attempts:
            try:
                return AstrologicalSubject(*base_args, **extra)
            except TypeError:
                continue

    return AstrologicalSubject(*base_args)


def _body(subject: Any, name: str) -> Dict[str, Any]:
    body = _get(subject, name)
    return {
        "sign": _serialize(_field(body, ("sign", "sign_name", "zodiac_sign"))),
        "deg": _serialize(_field(body, ("position", "pos", "degree", "abs_pos"))),
        "house": _serialize(_field(body, ("house", "house_name"))),
        "retrograde": bool(_field(body, ("retrograde", "is_retrograde")) or False),
    }


def _angle(subject: Any, name: str) -> Dict[str, Any]:
    angle = _get(subject, name)
    return {
        "sign": _serialize(_field(angle, ("sign", "sign_name", "zodiac_sign"))),
        "deg": _serialize(_field(angle, ("position", "pos", "degree", "abs_pos"))),
    }


def _aspects(subject: Any) -> Iterable[Dict[str, Any]]:
    if callable(getattr(subject, "aspects", None)):
        return [_normalize_aspect(item) for item in subject.aspects()]

    candidates = []
    try:
        from kerykeion import NatalAspects

        candidates.append(NatalAspects)
    except ImportError:
        pass

    try:
        from kerykeion.aspects.natal_aspects import NatalAspects

        candidates.append(NatalAspects)
    except ImportError:
        pass

    for aspects_cls in candidates:
        try:
            aspects = aspects_cls(subject)
            raw = (
                getattr(aspects, "relevant_aspects", None)
                or getattr(aspects, "all_aspects", None)
                or getattr(aspects, "aspects", None)
                or []
            )
            return [_normalize_aspect(item) for item in raw]
        except Exception:
            continue

    return []


def _normalize_aspect(item: Any) -> Dict[str, Any]:
    return {
        "p1": _serialize(_field(item, ("p1_name", "planet1", "first", "body1", "p1"))),
        "p2": _serialize(_field(item, ("p2_name", "planet2", "second", "body2", "p2"))),
        "aspect": _serialize(_field(item, ("aspect", "aspect_name", "name"))),
        "orb": _serialize(_field(item, ("orbit", "orb"))),
        "degrees": _serialize(_field(item, ("aspect_degrees", "degrees", "angle"))),
    }


def _numerology(year: int, month: int, day: int, name: str) -> Dict[str, Any]:
    compact_date = f"{year:04d}{month:02d}{day:02d}"
    life_path = _digital_root(sum(int(char) for char in compact_date), keep_masters=True)
    birth_day = _digital_root(day, keep_masters=True)
    name_seed = sum(ord(char.lower()) for char in name if char.strip())

    return {
        "life_path": life_path,
        "birth_day": birth_day,
        "name_number": _digital_root(name_seed),
    }


def _saju(year: int, month: int, day: int, hour: int) -> Dict[str, Any]:
    birth = date(year, month, day)
    year_index = (year - 1984) % 60
    month_index = (year * 12 + month + 14) % 60
    day_index = (birth.toordinal() + 15) % 60
    hour_branch_index = ((hour + 1) // 2) % 12
    hour_index = (day_index * 12 + hour_branch_index) % 60

    return {
        "year_pillar": _pillar(year_index),
        "month_pillar": _pillar(month_index),
        "day_pillar": _pillar(day_index),
        "hour_pillar": _pillar(hour_index),
    }


def _pillar(index: int) -> Dict[str, str]:
    return {
        "stem": STEMS[index % 10],
        "branch": BRANCHES[index % 12],
    }


def _digital_root(value: int, keep_masters: bool = False) -> int:
    while value > 9 and not (keep_masters and value in (11, 22, 33)):
        value = sum(int(char) for char in str(value))
    return value


def _input_hash(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    city: str,
    country: str,
) -> str:
    source = f"{year:04d}-{month:02d}-{day:02d}|{hour:02d}:{minute:02d}|{city.strip().lower()}|{country.strip().lower()}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _field(item: Any, names: Iterable[str]) -> Any:
    if item is None:
        return None

    if isinstance(item, dict):
        for name in names:
            if name in item:
                return item[name]

    if hasattr(item, "model_dump"):
        dumped = item.model_dump()
        for name in names:
            if name in dumped:
                return dumped[name]

    for name in names:
        if hasattr(item, name):
            return getattr(item, name)

    return None


def _get(item: Any, name: str) -> Any:
    if isinstance(item, dict):
        return item.get(name)
    return getattr(item, name)


def _has(item: Any, name: str) -> bool:
    if isinstance(item, dict):
        return name in item
    return hasattr(item, name)


def _serialize(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "value"):
        return value.value
    return str(value)


def _float_or_none(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    return float(value)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self._send_json({"ok": True}, status=204)

    def do_POST(self) -> None:
        try:
            content_length = int(self.headers.get("content-length", 0))
            payload = json.loads(self.rfile.read(content_length) or b"{}")
            self._send_json(chart_from_payload(payload))
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Read JSON payload from stdin")
    args = parser.parse_args()

    if args.json:
        payload = json.loads(input())
        print(json.dumps(chart_from_payload(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
