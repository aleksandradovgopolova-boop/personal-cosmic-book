# Personal Cosmic Book

Сервис генерации персональных digital-книг: полная книга для себя и подарочная книга для близкого человека.

## Первый MVP

- Next.js 14 App Router UI: витрина персональной книги.
- `api/chart.py`: Vercel Python Serverless endpoint для расчета карты через `kerykeion`.
- `supabase/migrations/001_initial_schema.sql`: стартовая схема БД, RLS и bucket для книг.
- `prompts/`: версионируемые промпты синтеза паттернов и полной книги.

## Локальный запуск

```bash
pnpm install
pnpm dev
```

Проверка Python-расчета:

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest tests/test_chart.py
```

## Supabase + генерация книги

Чтобы подготовить окружение для платной книги:

1. Заполните `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`.
2. Примените миграцию `supabase/migrations/001_initial_schema.sql`.
3. Подключите оплату и генерацию полной книги после статуса `paid`.

## Следующие интеграции

1. Supabase Auth + сохранение `orders`, `chart_data`, `books`.
2. ЮKassa checkout + webhook `paid`.
3. Генерация полной книги и загрузка HTML в Supabase Storage.
