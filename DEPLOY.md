# Деплой Personal Cosmic Book

Проект разворачивается на любом хостинге с Python 3.11+ (российский VPS,
Timeweb Cloud, Selectel, Yandex Cloud и т.д.). `server.py` в одном процессе
отдаёт статический сайт из `public/` и JSON-эндпоинты `/api/chart`,
`/api/book`, `/api/checkout`. Внешний фронтенд-фреймворк для прода не нужен.

> Vercel не используем: для российской аудитории и приёма платежей через
> ЮKassa нужен хостинг с доступом из РФ.

## Переменные окружения

Скопируй `.env.example` в `.env` и заполни:

| Переменная | Зачем |
|---|---|
| `DEEPSEEK_API_KEY` | генерация текста книги (без ключа — детерминированный шаблон) |
| `DEEPSEEK_MODEL` | по умолчанию `deepseek-chat` |
| `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY` | реальная оплата (без них — демо-подтверждение) |
| `NEXT_PUBLIC_APP_URL` | публичный адрес сайта (return_url для оплаты) |
| `PORT`, `HOST` | порт/хост сервера (по умолчанию `0.0.0.0:8000`) |

Астрология (планеты и дома) считается через `kerykeion` — он ставится из
`requirements.txt`. Без него нумерология, Ба-цзы и тема по знаку Солнца всё
равно работают.

## Вариант 1. Docker (рекомендуется)

```bash
cp .env.example .env    # заполнить ключи
docker compose up -d --build
```

Сайт поднимется на `http://SERVER_IP:8000`. Обнови:

```bash
git pull && docker compose up -d --build
```

Без compose:

```bash
docker build -t personal-cosmic-book .
docker run -d --env-file .env -p 8000:8000 --restart unless-stopped personal-cosmic-book
```

## Вариант 2. Напрямую на VPS (без Docker)

```bash
sudo apt-get update && sudo apt-get install -y python3 python3-venv build-essential
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # заполнить ключи
set -a && . ./.env && set +a
python server.py
```

### systemd (автозапуск)

`/etc/systemd/system/pcb.service`:

```ini
[Unit]
Description=Personal Cosmic Book
After=network.target

[Service]
WorkingDirectory=/opt/personal-cosmic-book
EnvironmentFile=/opt/personal-cosmic-book/.env
ExecStart=/opt/personal-cosmic-book/.venv/bin/python server.py
Restart=always
User=www-data

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now pcb
```

## Nginx (домен + HTTPS)

Проксируй домен на сервер и получи сертификат (certbot):

```nginx
server {
    server_name personal-cosmic-book.ru;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

После смены домена обнови `NEXT_PUBLIC_APP_URL` в `.env` и canonical/OG-теги в
`public/landing.html`.

## Проверка после деплоя

```bash
curl -s http://SERVER_IP:8000/ | grep -o '<title>[^<]*</title>'
curl -s -X POST http://SERVER_IP:8000/api/book \
  -H 'Content-Type: application/json' \
  -d '{"name":"Тест","date":"20.06.1996","city":"Москва","requested_theme":"auto"}' | head -c 400
```
