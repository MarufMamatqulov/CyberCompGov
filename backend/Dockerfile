FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN useradd --create-home --uid 1000 app && chown -R app /app
USER app

EXPOSE 8000
# Seed bitta jarayonda bajariladi, so‘ng bir nechta uvicorn worker ishga tushadi
CMD ["sh", "-c", "python -m app.seed.seed && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS:-2} --proxy-headers --forwarded-allow-ips='*'"]
