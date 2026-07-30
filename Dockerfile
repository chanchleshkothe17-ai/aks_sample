# ---- Build stage: has pip/setuptools, installs dependencies only ----
FROM python:3.12-alpine AS builder

WORKDIR /app
COPY requirements.txt .
# Install into an isolated prefix so the runtime stage can copy just this,
# without pulling pip/setuptools/wheel (or pip's vendored msgpack) along with it.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime stage: no pip, no setuptools, no build tools at all ----
FROM python:3.12-alpine AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

RUN apk upgrade --no-cache && addgroup -S -g 10001 app && adduser -S -D -H -u 10001 -G app app

# Only the installed packages come across — not pip itself.
COPY --from=builder /install /usr/local
COPY app ./app
USER 10001:10001

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
