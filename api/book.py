from __future__ import annotations

import json
import os
import ssl
import urllib.request
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional

try:
    from .chart import chart_from_payload
except Exception:  # pragma: no cover - allow running as a script
    from chart import chart_from_payload


# The 19 sections of the full book (mirrors paidBookSections in lib/products.ts).
BOOK_SECTIONS = [
    "Космический портрет",
    "Характер и внутренняя опора",
    "Сильные стороны",
    "Внутренние противоречия",
    "Эмоции и реакции",
    "Отношения и близость",
    "Деньги и самоценность",
    "Предназначение и работа",
    "Жизненные уроки",
    "Периоды перемен",
    "Родовые темы",
    "Тень и защитные сценарии",
    "Таланты и ресурсы",
    "Как тебя видят другие",
    "Практики поддержки",
    "Личная формула",
    "Письмо себе",
    "План бережных шагов",
    "Главные инсайты",
]

# Canonical sign key normalization: kerykeion may return 3-letter codes or full
# English names; we also accept Russian.
SIGN_ALIASES = {
    "ari": "aries", "aries": "aries", "овен": "aries",
    "tau": "taurus", "taurus": "taurus", "телец": "taurus",
    "gem": "gemini", "gemini": "gemini", "близнецы": "gemini",
    "can": "cancer", "cancer": "cancer", "рак": "cancer",
    "leo": "leo", "лев": "leo",
    "vir": "virgo", "virgo": "virgo", "дева": "virgo",
    "lib": "libra", "libra": "libra", "весы": "libra",
    "sco": "scorpio", "scorpio": "scorpio", "скорпион": "scorpio",
    "sag": "sagittarius", "sagittarius": "sagittarius", "стрелец": "sagittarius",
    "cap": "capricorn", "capricorn": "capricorn", "козерог": "capricorn",
    "aqu": "aquarius", "aquarius": "aquarius", "водолей": "aquarius",
    "pis": "pisces", "pisces": "pisces", "рыбы": "pisces",
}

SIGN_RU = {
    "aries": "Овен", "taurus": "Телец", "gemini": "Близнецы", "cancer": "Рак",
    "leo": "Лев", "virgo": "Дева", "libra": "Весы", "scorpio": "Скорпион",
    "sagittarius": "Стрелец", "capricorn": "Козерог", "aquarius": "Водолей",
    "pisces": "Рыбы",
}

SUN_TEXT = {
    "aries": "В тебе живёт первопроходец. Ты чувствуешь жизнь как движение и плохо переносишь застой — тебе нужно начинать, пробовать, идти первой. Смелость даётся тебе легче, чем терпение, и в этом одновременно твоя сила и твой урок.",
    "taurus": "Ты создана из надёжности и вкуса к жизни. Тебе важно опираться на что-то устойчивое — тело, дом, привычный ритм. Ты не спешишь, но то, что ты строишь, остаётся надолго. Твоя ценность не в скорости, а в глубине корней.",
    "gemini": "В тебе много воздуха: ум быстро связывает факты, а любопытство ведёт от темы к теме. Тебе нужно, чтобы жизнь оставалась живой и разнообразной. Твой дар — соединять людей и идеи, твой вызов — доводить начатое до глубины.",
    "cancer": "Ты чувствуешь мир кожей. Забота, память, привязанность — твой родной язык. Ты умеешь создавать тепло, в котором другим хочется остаться. Твоя задача — научиться давать столько же бережности себе, сколько ты отдаёшь близким.",
    "leo": "В тебе есть внутреннее солнце — потребность светить, творить, быть заметной. Тебе важно, чтобы жизнь была яркой и настоящей. Твоя щедрость согревает, а твой урок — позволить себе быть любимой не за достижения, а просто так.",
    "virgo": "Ты видишь детали, которых не замечают другие, и хочешь, чтобы вокруг было чисто, точно, по-настоящему. Твоя внимательность — форма любви. Учишься ты одному: что «достаточно хорошо» — это уже хорошо, и себя тоже можно не доделывать.",
    "libra": "Тебе важны гармония, красота и справедливость. Ты чувствуешь чужие состояния и умеешь мирить противоположности. Твой дар — держать баланс, твой вызов — не терять в этом балансе саму себя и своё «хочу».",
    "scorpio": "В тебе есть глубина, которая не выносит поверхностного. Ты доходишь до сути, проживаешь чувства до дна и умеешь перерождаться. Твоя сила — в честности с собой, твой урок — доверять и отпускать контроль.",
    "sagittarius": "Тебе нужен горизонт. Смыслы, дороги, свобода — то, что делает тебя живой. Ты умеешь верить в лучшее и заражать этим других. Твой вызов — соединить свободу с близостью, не путая обязательства с клеткой.",
    "capricorn": "В тебе живёт внутренняя опора и цель. Ты умеешь идти долго, брать ответственность и строить то, что выдержит время. Твоя сила — зрелость, твой урок — разрешить себе быть не только сильной, но и живой, уставшей, настоящей.",
    "aquarius": "Ты видишь мир немного иначе, чем принято, и это нормально. Свобода, идеи, честность важнее для тебя, чем удобство. Твой дар — быть собой в мире шаблонов, твой вызов — не прятать тепло за отстранённостью.",
    "pisces": "Ты тонко чувствуешь то, что между строк. Сострадание, воображение, связь с чем-то большим — твоя стихия. Твой дар — исцелять присутствием, твой урок — выстраивать границы, чтобы не растворяться в чужом.",
}

SIGN_TRAIT = {
    "aries": "прямоту и живой огонь", "taurus": "спокойствие и верность",
    "gemini": "лёгкость и любопытство", "cancer": "теплоту и чуткость",
    "leo": "щедрость и достоинство", "virgo": "внимательность и заботу",
    "libra": "тактичность и чувство меры", "scorpio": "глубину и честность",
    "sagittarius": "открытость и веру", "capricorn": "сдержанность и надёжность",
    "aquarius": "независимость и оригинальность", "pisces": "мягкость и сострадание",
}

LIFE_PATH_TEXT = {
    1: "Твой путь — про самостоятельность и умение быть началом. Тебе важно найти своё направление и идти им, даже если рядом никто не идёт.",
    2: "Твой путь — про связь, чуткость и сотрудничество. Ты сильна не в одиночку, а рядом; твоя задача — ценить свою мягкость как силу, а не слабость.",
    3: "Твой путь — про выражение себя. Слово, творчество, радость — то, через что ты оживаешь. Тебе важно не прятать свой голос.",
    4: "Твой путь — про опору и созидание. Ты умеешь строить основательно; твоя задача — не превратить надёжность в клетку и оставить место лёгкости.",
    5: "Твой путь — про свободу и перемены. Тебе нужен простор и опыт; твоя задача — найти в движении свою внутреннюю ось.",
    6: "Твой путь — про любовь, заботу и ответственность за близких. Тебе важно научиться заботиться о других, не забывая о себе.",
    7: "Твой путь — про глубину и поиск смысла. Тебе нужны тишина и понимание; твоя задача — доверять внутреннему знанию.",
    8: "Твой путь — про силу, ресурс и масштаб. Тебе важно научиться владеть своей мощью бережно, не через борьбу, а через устойчивость.",
    9: "Твой путь — про сострадание и отдачу. Ты чувствуешь общее; твоя задача — служить из полноты, а не из самоотречения.",
    11: "Твой путь — про интуицию и вдохновение. Ты тоньше чувствуешь мир; твоя задача — заземлять свет в простые дела.",
    22: "Твой путь — про большое созидание. Ты можешь строить то, что нужно многим; твоя задача — идти шаг за шагом, не пугаясь масштаба.",
    33: "Твой путь — про заботу и исцеление в большом. Твоя задача — беречь себя, отдавая тепло миру.",
}

ELEMENT_RU = {"Wood": "Дерево", "Fire": "Огонь", "Earth": "Земля", "Metal": "Металл", "Water": "Вода"}
ELEMENT_TEXT = {
    "Wood": "Твоя внутренняя стихия — Дерево: рост, гибкость, стремление вверх. Тебе важно развиваться и не застаиваться.",
    "Fire": "Твоя внутренняя стихия — Огонь: тепло, страсть, вдохновение. Ты оживаешь, когда есть смысл и азарт.",
    "Earth": "Твоя внутренняя стихия — Земля: устойчивость, забота, надёжность. Тебе важны опора и ощущение дома.",
    "Metal": "Твоя внутренняя стихия — Металл: ясность, форма, достоинство. Тебе важны честность и чёткие границы.",
    "Water": "Твоя внутренняя стихия — Вода: чувствительность, глубина, текучесть. Ты сильна в интуиции и адаптации.",
}


def _sign_key(value: Any) -> Optional[str]:
    if not value:
        return None
    return SIGN_ALIASES.get(str(value).strip().lower())


def _placement(chart: Dict[str, Any], body: str) -> Optional[str]:
    node = chart.get(body)
    if isinstance(node, dict):
        return _sign_key(node.get("sign"))
    return None


def _day_element(chart: Dict[str, Any]) -> Optional[str]:
    saju = chart.get("saju") or {}
    day = saju.get("day_pillar") or {}
    stem = str(day.get("stem") or "")
    parts = stem.split(" ")
    return parts[1] if len(parts) > 1 else None


def build_book(chart: Dict[str, Any]) -> Dict[str, Any]:
    subject = chart.get("subject") or {}
    name = subject.get("name") or "Дорогой человек"

    sun = _placement(chart, "sun")
    moon = _placement(chart, "moon")
    asc = _placement(chart, "asc")
    numerology = chart.get("numerology") or {}
    life_path = numerology.get("life_path")
    element = _day_element(chart)

    def sun_p() -> Optional[str]:
        return SUN_TEXT.get(sun) if sun else None

    def moon_p() -> Optional[str]:
        if not moon:
            return None
        return f"Луна в знаке {SIGN_RU[moon]} даёт тебе {SIGN_TRAIT[moon]} во внутреннем мире — так ты чувствуешь, восстанавливаешься и заботишься."

    def asc_p() -> Optional[str]:
        if not asc:
            return None
        return f"Асцендент в знаке {SIGN_RU[asc]} — это первое впечатление, которое ты производишь: люди считывают в тебе {SIGN_TRAIT[asc]}."

    def life_p() -> Optional[str]:
        return LIFE_PATH_TEXT.get(life_path) if life_path is not None else None

    def elem_p() -> Optional[str]:
        return ELEMENT_TEXT.get(element) if element else None

    # Chapter builders keyed by section title.
    def chapter(section: str) -> List[str]:
        base: List[Optional[str]] = []
        if section == "Космический портрет":
            base = [sun_p(), moon_p(), asc_p(), life_p()]
        elif section == "Характер и внутренняя опора":
            base = [sun_p(), elem_p()]
        elif section == "Сильные стороны":
            base = [sun_p(), life_p()]
        elif section == "Внутренние противоречия":
            base = ["В тебе живут разные силы, и это нормально: они не мешают, а дополняют друг друга.", moon_p(), sun_p()]
        elif section == "Эмоции и реакции":
            base = [moon_p(), elem_p()]
        elif section == "Отношения и близость":
            base = [moon_p(), asc_p()]
        elif section == "Деньги и самоценность":
            base = ["Деньги для тебя — про ощущение собственной ценности, а не только про цифры.", life_p()]
        elif section == "Предназначение и работа":
            base = [life_p(), sun_p()]
        elif section == "Жизненные уроки":
            base = [life_p()]
        elif section == "Периоды перемен":
            base = ["В твоей жизни есть ритм: за периодами покоя приходят перемены, и они не ломают, а обновляют тебя."]
        elif section == "Родовые темы":
            base = ["За тобой стоит род — истории и силы твоих предков живут в тебе как ресурс.", elem_p()]
        elif section == "Тень и защитные сценарии":
            base = ["Там, где было больно, ты научилась защищаться. Эти сценарии когда-то берегли тебя — сейчас их можно мягко пересмотреть.", moon_p()]
        elif section == "Таланты и ресурсы":
            base = [elem_p(), sun_p()]
        elif section == "Как тебя видят другие":
            base = [asc_p(), sun_p()]
        elif section == "Практики поддержки":
            base = ["Тебе важно иметь простые опоры на каждый день: то, что возвращает тебя к себе.", elem_p()]
        elif section == "Личная формула":
            parts = [SIGN_RU.get(sun or ""), (f"Луна {SIGN_RU[moon]}" if moon else None), (f"путь {life_path}" if life_path else None)]
            formula = " · ".join([p for p in parts if p])
            base = [f"Твоя короткая формула: {formula}." if formula else "Твоя формула складывается из уникального сочетания дат и знаков."]
        elif section == "Письмо себе":
            base = [f"{name}, ты не обязана быть удобной, чтобы быть любимой. Ты уже достаточно."]
        elif section == "План бережных шагов":
            base = ["Начни с малого: один честный шаг к себе в неделю. Не подвиг — а бережность."]
        elif section == "Главные инсайты":
            base = [sun_p(), life_p(), "Ты — целая. Эта книга лишь помогает тебе вспомнить то, что ты и так знаешь о себе."]
        else:
            base = []

        paragraphs = [p for p in base if p]
        if not paragraphs:
            paragraphs = [
                "Эта глава раскроется полнее, когда в карте будет больше точных данных о времени и месте рождения. "
                "Пока прими её как приглашение прислушаться к себе в этой теме."
            ]
        return paragraphs

    chapters = [{"title": title, "paragraphs": chapter(title)} for title in BOOK_SECTIONS]

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
        "cover": {
            "name": name,
            "date": subject.get("date"),
            "city": subject.get("city"),
            "tags": tags,
        },
        "chapters": chapters,
        "generated_with": "template",
        "astrology_available": bool(chart.get("astrology_available")),
    }


DEEPSEEK_SYSTEM = (
    "Ты создаёшь персональную цифровую книгу «Книга о тебе»: глубокий "
    "психологический портрет через язык астрологии, нумерологии, матрицы "
    "судьбы и саджу. Это не гороскоп, не предсказание и не обещание будущих "
    "событий, а бережный документ самопознания. Обращайся на «ты». Пиши тепло, "
    "по-взрослому и конкретно, без эзотерических клише и без обещаний. Каждый "
    "вывод: что это значит, как проявляется, что с этим можно делать. Одну "
    "мысль раскрывай один раз, не повторяйся между главами."
)


def _chart_facts(chart: Dict[str, Any]) -> str:
    lines: List[str] = []
    subject = chart.get("subject") or {}
    lines.append(f"Имя: {subject.get('name')}")
    lines.append(f"Дата рождения: {subject.get('date')}, время: {subject.get('time')}, город: {subject.get('city')}")

    if chart.get("astrology_available"):
        for body, label in (("sun", "Солнце"), ("moon", "Луна"), ("asc", "Асцендент"),
                            ("mercury", "Меркурий"), ("venus", "Венера"), ("mars", "Марс")):
            node = chart.get(body)
            if isinstance(node, dict) and node.get("sign"):
                key = _sign_key(node.get("sign"))
                lines.append(f"{label}: {SIGN_RU.get(key, node.get('sign'))}")

    num = chart.get("numerology") or {}
    if num:
        lines.append(f"Нумерология — число пути: {num.get('life_path')}, число имени: {num.get('name_number')}")

    element = _day_element(chart)
    if element:
        lines.append(f"Саджу — стихия дня: {ELEMENT_RU.get(element, element)}")

    return "\n".join(lines)


def _generate_with_deepseek(chart: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """Generate the 19 chapters via DeepSeek. Returns None on any failure."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return None

    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

    sections = "\n".join(f"{i + 1}. {title}" for i, title in enumerate(BOOK_SECTIONS))
    user_content = (
        "Данные человека:\n" + _chart_facts(chart) + "\n\n"
        "Напиши персональную книгу из ровно этих 19 глав, сохраняя их названия и порядок:\n"
        + sections + "\n\n"
        "Для каждой главы — 2–4 абзаца живого текста, опирающегося на данные выше. "
        "Верни строго JSON вида "
        '{"chapters":[{"title":"<название главы>","paragraphs":["<абзац>","<абзац>"]}]} '
        "без пояснений и без markdown."
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
        context = ssl.create_default_context()
        with urllib.request.urlopen(request, context=context, timeout=120) as response:
            data = json.load(response)
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        chapters = parsed.get("chapters")
        if not isinstance(chapters, list) or not chapters:
            return None
        cleaned: List[Dict[str, Any]] = []
        for item in chapters:
            title = str(item.get("title") or "").strip()
            paragraphs = [str(p).strip() for p in (item.get("paragraphs") or []) if str(p).strip()]
            if title and paragraphs:
                cleaned.append({"title": title, "paragraphs": paragraphs})
        return cleaned or None
    except Exception:
        return None


def generate_book(chart: Dict[str, Any]) -> Dict[str, Any]:
    """Build the book, using DeepSeek for the prose when configured."""
    book = build_book(chart)  # cover + deterministic template chapters (fallback)
    chapters = _generate_with_deepseek(chart)
    if chapters:
        book["chapters"] = chapters
        book["generated_with"] = "deepseek"
    return book


def book_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    chart = chart_from_payload(payload)
    book = generate_book(chart)
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
