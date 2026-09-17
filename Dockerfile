FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    HOST=0.0.0.0 \
    PORT=8000 \
    DATABASE_PATH=/app/data/flowboard.db

WORKDIR /app
RUN groupadd --system flowboard && useradd --system --gid flowboard --create-home flowboard
COPY --chown=flowboard:flowboard . .
RUN mkdir -p /app/data && chown flowboard:flowboard /app/data

USER flowboard
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=4s --start-period=8s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)" || exit 1

CMD ["python", "app.py"]
