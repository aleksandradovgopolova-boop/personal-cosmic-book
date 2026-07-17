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

# Offline coordinates for common cities, keyed by lowercased city name (RU + EN).
# Used first so the endpoint works without any network; the online geocoder below
# resolves anything else.
CITY_COORDS = {
    "moscow": {"lat": 55.7558, "lng": 37.6173, "tz": "Europe/Moscow"},
    "москва": {"lat": 55.7558, "lng": 37.6173, "tz": "Europe/Moscow"},
    "saint petersburg": {"lat": 59.9311, "lng": 30.3609, "tz": "Europe/Moscow"},
    "st petersburg": {"lat": 59.9311, "lng": 30.3609, "tz": "Europe/Moscow"},
    "санкт-петербург": {"lat": 59.9311, "lng": 30.3609, "tz": "Europe/Moscow"},
    "спб": {"lat": 59.9311, "lng": 30.3609, "tz": "Europe/Moscow"},
    "питер": {"lat": 59.9311, "lng": 30.3609, "tz": "Europe/Moscow"},
    "новосибирск": {"lat": 55.0084, "lng": 82.9357, "tz": "Asia/Novosibirsk"},
    "novosibirsk": {"lat": 55.0084, "lng": 82.9357, "tz": "Asia/Novosibirsk"},
    "екатеринбург": {"lat": 56.8389, "lng": 60.6057, "tz": "Asia/Yekaterinburg"},
    "yekaterinburg": {"lat": 56.8389, "lng": 60.6057, "tz": "Asia/Yekaterinburg"},
    "казань": {"lat": 55.7963, "lng": 49.1088, "tz": "Europe/Moscow"},
    "kazan": {"lat": 55.7963, "lng": 49.1088, "tz": "Europe/Moscow"},
    "нижний новгород": {"lat": 56.2965, "lng": 43.9361, "tz": "Europe/Moscow"},
    "челябинск": {"lat": 55.1644, "lng": 61.4368, "tz": "Asia/Yekaterinburg"},
    "самара": {"lat": 53.1959, "lng": 50.1002, "tz": "Europe/Samara"},
    "ростов-на-дону": {"lat": 47.2357, "lng": 39.7015, "tz": "Europe/Moscow"},
    "краснодар": {"lat": 45.0355, "lng": 38.9753, "tz": "Europe/Moscow"},
    "владивосток": {"lat": 43.1155, "lng": 131.8855, "tz": "Asia/Vladivostok"},
    "сочи": {"lat": 43.5855, "lng": 39.7231, "tz": "Europe/Moscow"},
    "калининград": {"lat": 54.7104, "lng": 20.4522, "tz": "Europe/Kaliningrad"},
    "киев": {"lat": 50.4501, "lng": 30.5234, "tz": "Europe/Kyiv"},
    "kyiv": {"lat": 50.4501, "lng": 30.5234, "tz": "Europe/Kyiv"},
    "kiev": {"lat": 50.4501, "lng": 30.5234, "tz": "Europe/Kyiv"},
    "минск": {"lat": 53.9006, "lng": 27.5590, "tz": "Europe/Minsk"},
    "minsk": {"lat": 53.9006, "lng": 27.5590, "tz": "Europe/Minsk"},
    "алматы": {"lat": 43.2220, "lng": 76.8512, "tz": "Asia/Almaty"},
    "almaty": {"lat": 43.2220, "lng": 76.8512, "tz": "Asia/Almaty"},
    "ташкент": {"lat": 41.2995, "lng": 69.2401, "tz": "Asia/Tashkent"},
    "тбилиси": {"lat": 41.7151, "lng": 44.8271, "tz": "Asia/Tbilisi"},
    "ереван": {"lat": 40.1792, "lng": 44.4991, "tz": "Asia/Yerevan"},
    "баку": {"lat": 40.4093, "lng": 49.8671, "tz": "Asia/Baku"},
    "new york": {"lat": 40.7128, "lng": -74.006, "tz": "America/New_York"},
    "london": {"lat": 51.5072, "lng": -0.1276, "tz": "Europe/London"},
    "paris": {"lat": 48.8566, "lng": 2.3522, "tz": "Europe/Paris"},
    "berlin": {"lat": 52.52, "lng": 13.405, "tz": "Europe/Berlin"},
    "istanbul": {"lat": 41.0082, "lng": 28.9784, "tz": "Europe/Istanbul"},
    "стамбул": {"lat": 41.0082, "lng": 28.9784, "tz": "Europe/Istanbul"},
    "dubai": {"lat": 25.2048, "lng": 55.2708, "tz": "Asia/Dubai"},
    "дубай": {"lat": 25.2048, "lng": 55.2708, "tz": "Asia/Dubai"},
}


def _geocode_online(city: str, country: str = "") -> Optional[Dict[str, Any]]:
    """Resolve a city to lat/lng/timezone via the free Open-Meteo geocoder.

    Returns None on any failure so the caller can degrade gracefully. Not used
    when offline coordinates already cover the city.
    """
    import json as _json
    import ssl as _ssl
    import urllib.parse as _urlparse
    import urllib.request as _urlreq

    query = city.strip()
    if not query:
        return None
    params = _urlparse.urlencode({"name": query, "count": 1, "language": "ru", "format": "json"})
    url = f"https://geocoding-api.open-meteo.com/v1/search?{params}"
    try:
        context = _ssl.create_default_context()
        request = _urlreq.Request(url, headers={"User-Agent": "personal-cosmic-book/1.0"})
        with _urlreq.urlopen(request, context=context, timeout=8) as response:
            data = _json.load(response)
    except Exception:
        return None

    results = data.get("results") or []
    if not results:
        return None
    top = results[0]
    if top.get("latitude") is None or top.get("longitude") is None:
        return None
    return {
        "lat": float(top["latitude"]),
        "lng": float(top["longitude"]),
        "tz": top.get("timezone") or "UTC",
    }


def _resolve_location(
    city: str,
    country: str,
    lat: Optional[float],
    lng: Optional[float],
    timezone: Optional[str],
) -> Dict[str, Optional[Any]]:
    """Best-effort coordinates+timezone so kerykeion can run offline."""
    if lat is not None and lng is not None:
        return {"lat": lat, "lng": lng, "tz": timezone or "UTC"}

    offline = CITY_COORDS.get(city.strip().lower())
    if offline:
        return {"lat": offline["lat"], "lng": offline["lng"], "tz": timezone or offline["tz"]}

    online = _geocode_online(city, country)
    if online:
        return {"lat": online["lat"], "lng": online["lng"], "tz": timezone or online["tz"]}

    return {"lat": None, "lng": None, "tz": timezone}

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

    chart: Dict[str, Any] = {
        "subject": {
            "name": name,
            "date": f"{year:04d}-{month:02d}-{day:02d}",
            "time": f"{hour:02d}:{minute:02d}",
            "city": city,
            "country": country,
        },
        "input_hash": _input_hash(year, month, day, hour, minute, city, country),
        "location": {"lat": lat, "lng": lng, "tz": timezone},
        "numerology": _numerology(year, month, day, name),
        "saju": _saju(year, month, day, hour),
    }

    # Numerology and Saju are always available (computed from the date).
    # Astrology needs kerykeion plus a resolvable birth location, so it may be
    # unavailable in some environments — degrade gracefully instead of failing.
    try:
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
        chart.update(bodies)
        chart["asc"] = _angle(subject, "first_house")
        chart["mc"] = _angle(subject, "tenth_house")
        chart["aspects"] = _aspects(subject)
        chart["astrology_available"] = True
    except Exception as exc:  # noqa: BLE001 - report, don't crash the endpoint
        chart["astrology_available"] = False
        chart["astrology_error"] = str(exc)

    return chart


def chart_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    birth_date = payload.get("date") or payload.get("birthDate")
    birth_time = payload.get("time") or payload.get("birthTime") or "12:00"
    if not birth_date:
        raise ValueError("date is required")

    year, month, day = _parse_date(str(birth_date))
    hour, minute = [int(part) for part in str(birth_time).split(":")[:2]]
    city = str(payload.get("city") or "")
    country = str(payload.get("country") or payload.get("nation") or "")

    location = _resolve_location(
        city=city,
        country=country,
        lat=_float_or_none(payload.get("lat")),
        lng=_float_or_none(payload.get("lng", payload.get("lon"))),
        timezone=payload.get("timezone") or payload.get("tz"),
    )

    return get_chart(
        name=str(payload.get("name") or "Subject"),
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city,
        country=country,
        lat=location["lat"],
        lng=location["lng"],
        timezone=location["tz"],
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


def _parse_date(value: str) -> "list[int]":
    """Accept both ISO 'YYYY-MM-DD' and 'DD.MM.YYYY'."""
    value = value.strip()
    if "." in value:
        day, month, year = [int(part) for part in value.split(".")[:3]]
        return [year, month, day]
    year, month, day = [int(part) for part in value.split("-")[:3]]
    return [year, month, day]


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
