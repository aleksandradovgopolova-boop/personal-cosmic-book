# Роутинг моделей

## Рекомендуемая конфигурация MVP

| Этап | Основная модель | Режим | Fallback |
|---|---|---|---|
| Pattern synthesis | `deepseek-v4-flash` | thinking enabled, high | `deepseek-v4-pro` |
| Book blueprint | `deepseek-v4-pro` | thinking enabled, high | повтор Pro с validator feedback |
| Section generation | `deepseek-v4-flash` | thinking disabled | `deepseek-v4-pro` non-thinking |
| Semantic QA | `deepseek-v4-pro` | thinking enabled, high | ручной bad-case review |
| Add-ons | тот же роутинг | по типу этапа | Pro |

## Почему так

- Самый дорогой по объему этап — написание текста. Его выгодно отдавать Flash.
- Синтез, архитектура и QA короткие, но влияют на весь результат. Здесь допустим Pro.
- Не использовать Kimi как основной генератор до сравнительного теста на собственном golden set.
- Kimi K2.6 можно оставить как fallback или A/B challenger для текста.

## Параметры DeepSeek

### Аналитические этапы

```json
{
  "model": "deepseek-v4-pro",
  "reasoning_effort": "high",
  "thinking": {"type": "enabled"},
  "response_format": {"type": "json_object"}
}
```

Не передавать `temperature` в thinking mode.

### Проза

```json
{
  "model": "deepseek-v4-flash",
  "thinking": {"type": "disabled"},
  "temperature": 0.6,
  "response_format": {"type": "json_object"}
}
```

Всегда проверять `finish_reason`, пустой `content` и JSON Schema локально.

## Параметры Kimi K2.6

```json
{
  "model": "kimi-k2.6",
  "thinking": {"type": "disabled"},
  "response_format": {
    "type": "json_schema",
    "json_schema": {}
  }
}
```

Для Kimi K2.6 не передавать произвольную температуру: в non-thinking mode она фиксирована моделью. Использовать Kimi structured output там, где схема поддерживается.

## Provider adapter

В коде должен быть единый интерфейс:

```text
generate(stage, payload, schema, provider, model, mode)
```

Adapter отвечает за:

- различия параметров thinking;
- JSON mode / JSON Schema;
- timeout и retry;
- token usage и стоимость;
- cache key;
- логирование prompt version;
- сохранение bad cases.

## Что не использует LLM

Element profile, назначение `resolved_theme`, загрузка design tokens, генерация SVG-pattern и HTML/PDF rendering выполняются кодом. Для этих операций запрещено вызывать DeepSeek, Kimi или другую модель.

Изменение model provider, model version или prompt version не должно менять тему уже созданной книги.
