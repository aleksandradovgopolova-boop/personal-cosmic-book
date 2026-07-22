from __future__ import annotations

import hashlib
import json
import os
import ssl
import urllib.request
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional

try:
    from .chart import chart_from_payload
    from .theme import assign_theme, theme_tokens, THEME_LABELS
except Exception:  # pragma: no cover - allow running as a script
    from chart import chart_from_payload
    from theme import assign_theme, theme_tokens, THEME_LABELS


# The 10 sections of the book (book-structure-10-sections.md). Cover, table of
# contents, intro and disclaimer are service pages, not sections.
SECTIONS = [
    {"id": "01_main_theme", "title": "Главная тема твоей книги"},
    {"id": "02_inner_world", "title": "Твой внутренний мир"},
    {"id": "03_strengths", "title": "Твои сильные стороны"},
    {"id": "04_inner_tensions", "title": "Внутренние противоречия"},
    {"id": "05_love", "title": "Любовь и близость"},
    {"id": "06_realization", "title": "Реализация, дело и деньги"},
    {"id": "07_outer_expression", "title": "Как ты проявляешься в мире"},
    {"id": "08_life_patterns", "title": "Повторяющиеся сценарии и точки роста"},
    {"id": "09_personal_formula", "title": "Твоя персональная формула"},
    {"id": "10_next_chapter", "title": "Твой следующий шаг"},
]
SECTION_IDS = [s["id"] for s in SECTIONS]

DISCLAIMER = (
    "Материалы носят исключительно развлекательный и информационный характер. "
    "Не являются научно обоснованными прогнозами."
)

SIGN_ALIASES = {
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
SIGN_RU = {
    "aries": "Овен", "taurus": "Телец", "gemini": "Близнецы", "cancer": "Рак",
    "leo": "Лев", "virgo": "Дева", "libra": "Весы", "scorpio": "Скорпион",
    "sagittarius": "Стрелец", "capricorn": "Козерог", "aquarius": "Водолей", "pisces": "Рыбы",
}
SIGN_TRAIT = {
    "aries": "прямоту и живой огонь", "taurus": "спокойствие и верность",
    "gemini": "лёгкость и любопытство", "cancer": "теплоту и чуткость",
    "leo": "щедрость и достоинство", "virgo": "внимательность и заботу",
    "libra": "тактичность и чувство меры", "scorpio": "глубину и честность",
    "sagittarius": "открытость и веру", "capricorn": "сдержанность и надёжность",
    "aquarius": "независимость и оригинальность", "pisces": "мягкость и сострадание",
}
SUN_TEXT = {
    "aries": "В тебе живёт первопроходец: жизнь ощущается как движение, тебе важно начинать и идти первой. Смелость даётся легче терпения — в этом и сила, и урок.",
    "taurus": "Ты опираешься на надёжность и вкус к жизни. Ты не спешишь, но то, что ты строишь, остаётся надолго. Твоя ценность — в глубине корней, а не в скорости.",
    "gemini": "В тебе много воздуха: ум быстро связывает факты, любопытство ведёт от темы к теме. Твой дар — соединять людей и идеи, вызов — доводить начатое до глубины.",
    "cancer": "Ты чувствуешь мир кожей: забота, память и привязанность — твой родной язык. Задача — давать себе столько же бережности, сколько ты отдаёшь близким.",
    "leo": "В тебе есть внутреннее солнце — потребность светить и создавать. Урок — позволить себе быть любимой не за достижения, а просто так.",
    "virgo": "Ты видишь детали, которых не замечают другие; внимательность — твоя форма любви. Учишься одному: «достаточно хорошо» — это уже хорошо.",
    "libra": "Тебе важны гармония, красота и справедливость. Дар — держать баланс, вызов — не терять в нём саму себя и своё «хочу».",
    "scorpio": "В тебе есть глубина, которой тесно в поверхностном. Сила — в честности с собой, урок — доверять и отпускать контроль.",
    "sagittarius": "Тебе нужен горизонт: смыслы, дороги, свобода делают тебя живой. Вызов — соединить свободу с близостью.",
    "capricorn": "В тебе живёт внутренняя опора и цель: ты умеешь идти долго и строить надолго. Урок — разрешить себе быть не только сильной, но и живой.",
    "aquarius": "Ты видишь мир немного иначе, и это нормально. Дар — быть собой среди шаблонов, вызов — не прятать тепло за отстранённостью.",
    "pisces": "Ты тонко чувствуешь то, что между строк. Дар — исцелять присутствием, урок — выстраивать границы, чтобы не растворяться в чужом.",
}
LIFE_PATH_TEXT = {
    1: "Твой путь — про самостоятельность и умение быть началом: найти своё направление и идти им, даже если рядом никто не идёт.",
    2: "Твой путь — про связь и сотрудничество: ценить свою мягкость как силу, а не слабость.",
    3: "Твой путь — про выражение себя: слово, творчество, радость. Тебе важно не прятать свой голос.",
    4: "Твой путь — про опору и созидание: не превратить надёжность в клетку и оставить место лёгкости.",
    5: "Твой путь — про свободу и перемены: найти в движении свою внутреннюю ось.",
    6: "Твой путь — про любовь и ответственность за близких: заботиться о других, не забывая о себе.",
    7: "Твой путь — про глубину и поиск смысла: доверять внутреннему знанию.",
    8: "Твой путь — про силу и масштаб: владеть своей мощью бережно, через устойчивость.",
    9: "Твой путь — про сострадание и отдачу: служить из полноты, а не из самоотречения.",
    11: "Твой путь — про интуицию и вдохновение: заземлять свет в простые дела.",
    22: "Твой путь — про большое созидание: идти шаг за шагом, не пугаясь масштаба.",
    33: "Твой путь — про заботу и исцеление в большом: беречь себя, отдавая тепло миру.",
}
ELEMENT_RU = {"Wood": "Дерево", "Fire": "Огонь", "Earth": "Земля", "Metal": "Металл", "Water": "Вода"}
ELEMENT_TEXT = {
    "Wood": "Твоя внутренняя стихия — Дерево: рост, гибкость, стремление вверх. Тебе важно развиваться и не застаиваться.",
    "Fire": "Твоя внутренняя стихия — Огонь: тепло, страсть, вдохновение. Ты оживаешь, когда есть смысл и азарт.",
    "Earth": "Твоя внутренняя стихия — Земля: устойчивость и забота. Тебе важны опора и ощущение дома.",
    "Metal": "Твоя внутренняя стихия — Металл: ясность, форма, достоинство. Тебе важны честность и границы.",
    "Water": "Твоя внутренняя стихия — Вода: чувствительность и глубина. Ты сильна в интуиции и адаптации.",
}


def _sign_key(value: Any) -> Optional[str]:
    if not value:
        return None
    return SIGN_ALIASES.get(str(value).strip().lower())


def _placement(chart: Dict[str, Any], body: str) -> Optional[str]:
    node = chart.get(body)
    return _sign_key(node.get("sign")) if isinstance(node, dict) else None


def _day_element(chart: Dict[str, Any]) -> Optional[str]:
    stem = str(((chart.get("saju") or {}).get("day_pillar") or {}).get("stem") or "")
    parts = stem.split(" ")
    return parts[1] if len(parts) > 1 else None


# Sun sign depends only on the date (not birth time). Used so the visual theme
# (chosen from the Sun-sign element) works even without full astrology.
_SUN_CUTOFFS = [
    (20, "capricorn"), (19, "aquarius"), (20, "pisces"), (20, "aries"),
    (21, "taurus"), (21, "gemini"), (22, "cancer"), (23, "leo"),
    (23, "virgo"), (23, "libra"), (22, "scorpio"), (22, "sagittarius"),
]


def _sun_sign_from_date(date_iso: Any) -> Optional[str]:
    try:
        parts = [int(x) for x in str(date_iso).split("-")[:3]]
        month, day = parts[1], parts[2]
    except Exception:
        return None
    if not 1 <= month <= 12:
        return None
    cut_day, sign = _SUN_CUTOFFS[month - 1]
    return sign if day <= cut_day else _SUN_CUTOFFS[month % 12][1]


def _block(paragraphs: List[Optional[str]], heading: Optional[str] = None) -> Optional[Dict[str, Any]]:
    clean = [p for p in paragraphs if p]
    if not clean:
        return None
    block: Dict[str, Any] = {"paragraphs": clean}
    if heading:
        block["heading"] = heading
    return block


def _template_sections(chart: Dict[str, Any]) -> List[Dict[str, Any]]:
    subject = chart.get("subject") or {}
    name = subject.get("name") or "Дорогой человек"
    sun = _placement(chart, "sun")
    moon = _placement(chart, "moon")
    asc = _placement(chart, "asc")
    life_path = (chart.get("numerology") or {}).get("life_path")
    element = _day_element(chart)

    sun_p = SUN_TEXT.get(sun) if sun else None
    moon_p = (f"Луна в знаке {SIGN_RU[moon]} даёт тебе {SIGN_TRAIT[moon]} во внутреннем мире — так ты чувствуешь и восстанавливаешься." if moon else None)
    asc_p = (f"Асцендент в знаке {SIGN_RU[asc]}: люди при первой встрече считывают в тебе {SIGN_TRAIT[asc]}." if asc else None)
    life_p = LIFE_PATH_TEXT.get(life_path) if life_path is not None else None
    elem_p = ELEMENT_TEXT.get(element) if element else None

    formula_parts = [SIGN_RU.get(sun or ""), (f"Луна {SIGN_RU[moon]}" if moon else None), (f"путь {life_path}" if life_path else None), (ELEMENT_RU.get(element or "") or None)]
    formula = " · ".join([p for p in formula_parts if p]) or "уникальное сочетание твоих дат и знаков"

    content = {
        "01_main_theme": [_block([sun_p, life_p])],
        "02_inner_world": [_block([moon_p, elem_p])],
        "03_strengths": [_block([sun_p, life_p])],
        "04_inner_tensions": [_block(["В тебе живут разные силы, и это нормально: они не мешают, а дополняют друг друга.", moon_p])],
        "05_love": [_block([moon_p, asc_p, "Формулируй это как вероятные механизмы близости, а не как готовый сценарий отношений."])],
        "06_realization": [_block(["В деле тебе важно чувствовать смысл и собственную ценность, а не только результат.", life_p, sun_p])],
        "07_outer_expression": [_block([asc_p, sun_p])],
        "08_life_patterns": [_block(["Там, где было больно, ты научилась защищаться. Эти сценарии когда-то берегли тебя — сейчас их можно мягко пересмотреть.", "Замечай цепочку: триггер — реакция — короткая выгода — долгая цена. В этом промежутке и живёт выбор."])],
        "09_personal_formula": [_block([f"Твоя короткая формула: {formula}.", "Это не четыре отдельные системы, а один портрет, собранный из согласий и различий между ними."])],
        "10_next_chapter": [
            _block([f"{name}, ты не обязана быть удобной, чтобы быть любимой. Ты уже достаточно."], heading="Письмо себе"),
            _block(["Начни с малого: один честный шаг к себе в неделю. Не подвиг — а бережность.", "Первый шаг на 24 часа: сделай сегодня одно небольшое действие в свою сторону."], heading="Бережные шаги"),
        ],
    }

    sections = []
    for meta in SECTIONS:
        blocks = [b for b in content.get(meta["id"], []) if b]
        if not blocks:
            blocks = [{"paragraphs": ["Эта глава раскроется полнее в полной версии книги, когда в карте будет больше точных данных."]}]
        sections.append({"id": meta["id"], "title": meta["title"], "blocks": blocks})
    return sections


def _cover(chart: Dict[str, Any]) -> Dict[str, Any]:
    subject = chart.get("subject") or {}
    sun = _placement(chart, "sun")
    moon = _placement(chart, "moon")
    asc = _placement(chart, "asc")
    life_path = (chart.get("numerology") or {}).get("life_path")
    tags = []
    if sun:
        tags.append(f"Солнце {SIGN_RU[sun]}")
    if moon:
        tags.append(f"Луна {SIGN_RU[moon]}")
    if asc:
        tags.append(f"AC {SIGN_RU[asc]}")
    if life_path is not None:
        tags.append(f"Путь {life_path}")
    return {
        "name": subject.get("name") or "Твоя книга",
        "title": "Книга о тебе",
        "subtitle": "персональный портрет по натальной карте",
        "date": subject.get("date"),
        "city": subject.get("city"),
        "gift_message": None,
        "tags": tags,
    }


def build_book(
    chart: Dict[str, Any],
    *,
    requested_theme: str = "auto",
    book_id: str = "",
    sections: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    if not book_id:
        book_id = str(chart.get("input_hash") or "")[:16] or "book"

    time_known = bool((chart.get("subject") or {}).get("time")) and not str((chart.get("subject") or {}).get("birthtime_status") or "").lower() == "unknown"
    angles_allowed = bool(chart.get("astrology_available")) and isinstance(chart.get("asc"), dict) and time_known

    # The theme is chosen from the Sun-sign element, which depends only on the
    # date. Ensure the Sun sign is present even when full astrology is missing.
    theme_chart = chart
    if not (isinstance(chart.get("sun"), dict) and chart["sun"].get("sign")):
        sun_sign = _sun_sign_from_date((chart.get("subject") or {}).get("date"))
        if sun_sign:
            theme_chart = {**chart, "sun": {"sign": sun_sign}}

    visual = assign_theme(
        theme_chart,
        requested_theme=requested_theme,
        book_id=book_id,
        angles_allowed=angles_allowed,
        moon_reliable=time_known,
    )
    theme = visual["resolved_theme"]
    tokens = theme_tokens(theme)

    return {
        "book_id": book_id,
        "resolved_theme": theme,
        "theme_label": THEME_LABELS.get(theme),
        "theme_tokens": tokens,
        "element_symbol": tokens["symbol"],
        "signature_seed": hashlib.sha256(book_id.encode("utf-8")).hexdigest()[:16],
        "visual_assignment": visual,
        "cover": _cover(chart),
        "sections": sections if sections is not None else _template_sections(chart),
        "disclaimer": DISCLAIMER,
        "astrology_available": bool(chart.get("astrology_available")),
        "generated_with": "template" if sections is None else "deepseek",
    }


# ── DeepSeek generation (analytics only — never gets theme/design data) ──
DEEPSEEK_SYSTEM = (
    "Ты — автор персональной цифровой книги «Книга о тебе»: тёплый, взрослый и "
    "конкретный текст самопознания на русском. Это не гороскоп, не диагноз и не "
    "предсказание. Обращайся на «ты». Каждый блок: внутренний механизм, вероятное "
    "проявление, ресурс, риск и мягкий практический вывод — как гипотезы, а не "
    "биография. Не пересказывай отдельно астрологию, нумерологию и саджу: пиши о "
    "человеке. Одну мысль раскрывай один раз, без повторов между разделами."
)


def _chart_facts(chart: Dict[str, Any]) -> str:
    lines: List[str] = []
    subject = chart.get("subject") or {}
    lines.append(f"Имя: {subject.get('name')}")
    lines.append(f"Дата: {subject.get('date')}, время: {subject.get('time')}, город: {subject.get('city')}")
    if chart.get("astrology_available"):
        for body, label in (("sun", "Солнце"), ("moon", "Луна"), ("asc", "Асцендент"), ("mercury", "Меркурий"), ("venus", "Венера"), ("mars", "Марс")):
            node = chart.get(body)
            if isinstance(node, dict) and node.get("sign"):
                lines.append(f"{label}: {SIGN_RU.get(_sign_key(node.get('sign')), node.get('sign'))}")
    num = chart.get("numerology") or {}
    if num:
        lines.append(f"Нумерология — путь: {num.get('life_path')}, имя: {num.get('name_number')}")
    element = _day_element(chart)
    if element:
        lines.append(f"Саджу — стихия дня: {ELEMENT_RU.get(element, element)}")
    return "\n".join(lines)


def _generate_sections_with_deepseek(chart: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return None
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

    section_list = "\n".join(f'{s["id"]} — {s["title"]}' for s in SECTIONS)
    user_content = (
        "Данные человека (только как основание, не пересказывай их списком):\n"
        + _chart_facts(chart) + "\n\n"
        "Напиши книгу ровно из этих 10 разделов, сохраняя id, названия и порядок:\n"
        + section_list + "\n\n"
        "Разделы 1–9 по 450–750 слов, раздел 10 — 800–1200 слов с 5 инсайтами, "
        "планом на 30 дней, первым шагом на 24 часа и письмом себе.\n"
        "Верни строго JSON: "
        '{"sections":[{"id":"01_main_theme","title":"...","eyebrow":"...",'
        '"opening":"...","blocks":[{"heading":"...","paragraphs":["...","..."]}],'
        '"reflection":{"title":"...","text":"..."}}]} без markdown.'
    )

    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": DEEPSEEK_SYSTEM},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.6,
        "response_format": {"type": "json_object"},
        "max_tokens": 8000,
    }).encode("utf-8")

    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, context=ssl.create_default_context(), timeout=120) as response:
            data = json.load(response)
        parsed = json.loads(data["choices"][0]["message"]["content"])
        raw = parsed.get("sections")
        if not isinstance(raw, list):
            return None
        by_id = {str(item.get("id")): item for item in raw if isinstance(item, dict)}
        sections = []
        for meta in SECTIONS:  # enforce exactly 10 in canonical order
            item = by_id.get(meta["id"], {})
            blocks = []
            for b in (item.get("blocks") or []):
                paras = [str(p).strip() for p in (b.get("paragraphs") or []) if str(p).strip()]
                if paras:
                    block = {"paragraphs": paras}
                    if b.get("heading"):
                        block["heading"] = str(b["heading"]).strip()
                    blocks.append(block)
            if not blocks:
                return None  # incomplete generation -> fall back to template
            section = {"id": meta["id"], "title": item.get("title") or meta["title"], "blocks": blocks}
            if item.get("eyebrow"):
                section["eyebrow"] = str(item["eyebrow"]).strip()
            if item.get("opening"):
                section["opening"] = str(item["opening"]).strip()
            if isinstance(item.get("reflection"), dict) and item["reflection"].get("text"):
                section["reflection"] = {"title": item["reflection"].get("title") or "Вопрос к себе", "text": str(item["reflection"]["text"]).strip()}
            sections.append(section)
        return sections
    except Exception:
        return None


def generate_book(chart: Dict[str, Any], *, requested_theme: str = "auto", book_id: str = "") -> Dict[str, Any]:
    sections = _generate_sections_with_deepseek(chart)
    return build_book(chart, requested_theme=requested_theme, book_id=book_id, sections=sections)


def book_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    chart = chart_from_payload(payload)
    presentation = payload.get("presentation") or {}
    requested_theme = payload.get("requested_theme") or presentation.get("requested_theme") or "auto"
    book_id = payload.get("book_id") or str(chart.get("input_hash") or "")[:16]
    book = generate_book(chart, requested_theme=requested_theme, book_id=book_id)
    book["chart"] = chart
    return book


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self._send_json({"ok": True}, status=204)

    def do_POST(self) -> None:
        try:
            content_length = int(self.headers.get("content-length", 0))
            payload = json.loads(self.rfile.read(content_length) or b"{}")
            self._send_json(book_from_payload(payload))
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
    import sys

    payload = json.loads(sys.stdin.read() or "{}")
    print(json.dumps(book_from_payload(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
