# Этап 1: контракт входных данных v3

## Назначение

Все числовые и астрономические вычисления выполняются локально. Модель не вычисляет карту, числа, арканы, столпы, транзиты, совместимость и визуальную стихию.

Модель получает нормализованный `evidence_catalog`. Каждое наблюдение имеет уникальный ID. На следующих этапах модель может ссылаться только на существующие ID и не должна придумывать новые значения.

Данные оформления хранятся отдельно от аналитического payload и не влияют на содержание книги.

## Основная структура

```json
{
  "meta": {
    "schema_version": "3.0",
    "locale": "ru-RU",
    "generated_at": "2026-07-21T12:00:00Z",
    "book_id": "stable-book-id",
    "calculation_versions": {
      "astrology": "kerykeion-x.y.z",
      "numerology": "1.0",
      "destiny_matrix": "1.0",
      "saju": "1.0",
      "element_theme_assignment": "astrology-four-elements-v1"
    }
  },
  "subject": {
    "name": "Софья",
    "grammatical_gender": "feminine",
    "birthdate": "1994-10-06",
    "birthtime": "14:30",
    "birthtime_status": "exact",
    "birthplace": "Москва, Россия",
    "lat": 55.7558,
    "lon": 37.6173,
    "timezone": "Europe/Moscow"
  },
  "user_context": {
    "main_request": "Почему мне сложно выбирать себя в отношениях?",
    "current_focus": ["relationships", "self_realization"],
    "life_stage": "optional free text",
    "preferences": [],
    "facts_provided_by_user": []
  },
  "presentation": {
    "requested_theme": "auto",
    "cover_subtitle": null,
    "gift_message": null
  },
  "visual_assignment": {
    "algorithm_version": "astrology-four-elements-v1",
    "element_scores": {
      "earth": 3,
      "water": 7,
      "air": 5,
      "fire": 2
    },
    "dominant_element": "water",
    "resolved_theme": "water",
    "resolution_reason": "dominant_element",
    "tie_breaker": null,
    "warnings": []
  },
  "data_quality": {
    "overall": "high",
    "birthtime_reliability": "high",
    "houses_allowed": true,
    "angles_allowed": true,
    "hour_pillar_allowed": true,
    "warnings": []
  },
  "raw": {
    "astrology": {},
    "numerology": {},
    "saju": {},
    "destiny_matrix": {},
    "transits": null,
    "synastry": null
  },
  "evidence_catalog": [
    {
      "id": "AST.SUN.SIGN",
      "system": "astrology",
      "category": "core_identity",
      "label": "Солнце в Весах",
      "fact": "sun.sign=Libra",
      "interpretive_keywords": ["ориентация на баланс", "чувствительность к взаимности"],
      "usable_for": ["core_identity", "relationships"],
      "reliability": "high",
      "caveat": null
    }
  ]
}
```

## Разрешённые темы

`presentation.requested_theme` принимает только:

```text
auto | earth | water | air | fire
```

`visual_assignment.resolved_theme` принимает только:

```text
earth | water | air | fire
```

LLM не может добавлять новые темы или менять `resolved_theme`.

## Расчёт element profile

Автоматическое назначение темы выполняется локально по знакам выбранных объектов западной астрологической карты.

### Веса v1

| Объект | Вес |
|---|---:|
| Солнце | 3 |
| Луна | 3 |
| Асцендент | 2, только если разрешены angles |
| Меркурий | 2 |
| Венера | 2 |
| Марс | 2 |
| Юпитер | 1 |
| Сатурн | 1 |

Внешние планеты не участвуют в выборе визуальной темы v1.

### Соответствие знаков стихиям

- `fire`: Aries, Leo, Sagittarius;
- `earth`: Taurus, Virgo, Capricorn;
- `air`: Gemini, Libra, Aquarius;
- `water`: Cancer, Scorpio, Pisces.

### Правила качества

1. Не учитывать положение с `reliability = low | excluded`.
2. Если при неизвестном времени Луна может находиться в двух знаках, не учитывать её в element profile или применять отдельное версионированное правило ambiguous moon. Не угадывать.
3. Асцендент учитывается только при `angles_allowed = true`.
4. Саджу не участвует в четырёхстихийном визуальном назначении: в нём используются Wood, Fire, Earth, Metal, Water, и Metal/Wood нельзя произвольно преобразовывать в Air.
5. Нумерология и матрица судьбы не используются для выбора темы.

## Разрешение темы

1. Если пользователь выбрал `earth | water | air | fire`, сервер использует его выбор:
   - `resolved_theme = requested_theme`;
   - `resolution_reason = user_choice`.
2. Если выбрано `auto`, сервер берёт элемент с максимальным score:
   - `resolution_reason = dominant_element`.
3. При равенстве score:
   - сначала используется стихия Солнца, если она входит в число лидеров;
   - затем стихия Луны, если она надёжна и входит в число лидеров;
   - затем стабильный hash от `book_id`, выбирающий только среди лидирующих стихий.
4. Если валидных астрологических данных недостаточно, используется стабильный hash от `book_id` по четырём темам:
   - `resolution_reason = hash_fallback`;
   - в `warnings` добавляется причина.
5. Одинаковые входные данные и одинаковая версия алгоритма всегда дают одну тему.

## Разделение аналитики и presentation

В stage 2–4 не передавать:

- `presentation.requested_theme`;
- `visual_assignment`;
- цветовые токены;
- названия стихийных тем;
- декоративные параметры.

Исключение: `cover_subtitle` и `gift_message` используются только renderer-ом на соответствующих страницах.

Текст книги не должен подстраиваться под выбранную тему и превращать визуальную стихию в психологическую характеристику.

## Обязательные правила подготовки evidence catalog

1. Один evidence item = один проверяемый факт.
2. `id` стабилен между повторными генерациями одной карты.
3. Значение `fact` формируется кодом, не моделью.
4. `interpretive_keywords` берутся из версионируемого локального словаря трактовок.
5. Если время рождения неизвестно:
   - `birthtime_status = unknown`;
   - дома и углы не включаются в `evidence_catalog`;
   - часовой столп не используется;
   - соответствующие `*_allowed = false`.
6. Нельзя передавать модели пустые или нулевые значения как реальные признаки.
7. Пользовательские факты хранятся отдельно и не смешиваются с символическими системами.
8. Для прогноза обязателен рассчитанный блок `raw.transits` и отдельные evidence ID вида `TRN.*`.
9. Для совместимости обязательны два независимых профиля, `raw.synastry` и контекст отношений.

## Классы надёжности

- `high` — точный расчёт и надёжные исходные данные.
- `medium` — расчёт корректен, но исходные данные неполны.
- `low` — использовать только как осторожную гипотезу.
- `excluded` — не передавать в генерацию.
