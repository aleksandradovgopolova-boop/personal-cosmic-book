# Personal Cosmic Book — self-hosted image (VPS / Timeweb Cloud / any Docker host)
FROM python:3.11-slim

# Build deps for kerykeion / pyswisseph (native extension).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Runtime code only (no Next/tests/prompts needed to serve the site).
COPY api ./api
COPY public ./public
COPY server.py ./

ENV HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

CMD ["python", "server.py"]
