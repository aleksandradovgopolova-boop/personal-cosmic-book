# Больше не буду меньше

Самостоятельный веб-ридер цифровой книги. Проект изолирован от `Personal Cosmic Book` и готовится к отдельному размещению на Vercel.

## Документация

- [`docs/project-base.md`](docs/project-base.md) — позиционирование книги, голос, тексты и визуальные правила.
- [`docs/implementation-status.md`](docs/implementation-status.md) — что фактически реализовано сейчас и какие ограничения временные.
- [`docs/development-guide.md`](docs/development-guide.md) — карта кода, быстрые сценарии правок и обязательные проверки.
- [`docs/book-contents.md`](docs/book-contents.md) — утверждённые названия глав и состояние загруженных страниц.
- [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) — проверка перед публичным запуском.

Если документация расходится с интерфейсом, фактическую реализацию сначала проверять в `src/reader-app.jsx` и `src/reader.css`, а затем синхронизировать соответствующий документ.

## Структура

- `index.html` — HTML-точка входа.
- `src/reader-app.jsx` — интерфейс, навигация, оглавление и демо-покупка.
- `src/reader.css` — стили ридера.
- `public/pages/` — страницы книги в WebP.
- `public/media/` — вступительное видео.
- `public/fonts/` — локальные шрифты проекта.
- `public/icons/book-web-icons/` — библиотека рисованных SVG-элементов.
- `docs/` — продуктовая, редакционная и техническая документация.
- `supabase/migrations/` — таблицы прогресса чтения и прав доступа.
- `scripts/check-assets.mjs` — проверка отсутствующих и неиспользуемых файлов.
- `vercel.json` — настройки production-сборки и Vercel.

## Локальный запуск

Требуется Node.js 20.19+ или 22.12+.

```bash
npm install
npm run dev
```

Vite покажет локальный адрес, обычно `http://localhost:5173`.

## Проверка production-сборки

```bash
npm run build
npm run preview
```

Готовые файлы появляются в `dist/`. Команда сборки также проверяет, что все страницы и медиа существуют и используются.

## Supabase и прогресс чтения

Ридер сохраняет страницу в `localStorage` без регистрации. После входа по ссылке из email прогресс синхронизируется между устройствами через Supabase.

1. В Supabase открыть **SQL Editor**.
2. Выполнить файл `supabase/migrations/202606140001_reader_sync.sql`.
3. В **Authentication → URL Configuration** указать production-домен в `Site URL`.
4. В `Redirect URLs` добавить локальный и production-адреса, например:

```text
http://localhost:5173/**
https://your-domain.vercel.app/**
```

5. Создать `.env.local` по примеру `.env.example`.

```bash
cp .env.example .env.local
```

`VITE_SUPABASE_PUBLISHABLE_KEY` является публичным ключом браузерного приложения. Service role key в клиентский проект добавлять нельзя.

Таблица `book_entitlements` доступна пользователю только на чтение. Право на полную книгу должен создавать доверенный серверный webhook после реальной оплаты; текущая демо-оплата остаётся локальной.

## Размещение на Vercel

При импорте репозитория:

1. Оставить корень репозитория как **Root Directory**.
2. Оставить Framework Preset `Vite`.
3. Build Command: `npm run build`.
4. Output Directory: `dist`.
5. Добавить переменные окружения `VITE_SUPABASE_URL` и `VITE_SUPABASE_PUBLISHABLE_KEY`.

Эти параметры уже продублированы в `vercel.json`, поэтому проект можно разворачивать без дополнительных настроек.

Для публикации через CLI из корня репозитория:

```bash
vercel
```

## Служебные состояния

- Флаг просмотренного вступления: `bnbm_intro_seen_v3`.
- Состояние чтения и демо-покупки: `bnbm_state_v2`.

Чтобы снова увидеть вступительное видео во время тестирования, удалите `bnbm_intro_seen_v3` из Local Storage.
