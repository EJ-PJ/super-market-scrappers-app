# Flask API for the VPS (Hostinger KVM 1). The desktop app still uses main.py + PyInstaller
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# gunicorn only lives in the image, the desktop build doesn't need it
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn==23.0.0

COPY main.py .
COPY app ./app

RUN useradd --system --no-create-home appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/stores', timeout=4)" || exit 1

# KVM 1 = 1 vCPU: 2 workers with threads (searches are I/O bound, waiting on the store websites).
# Long timeout because one search calls 5 stores
CMD ["gunicorn", "main:app", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", "--threads", "8", "--worker-class", "gthread", \
     "--timeout", "90", "--graceful-timeout", "30", \
     "--access-logfile", "-", "--error-logfile", "-"]
