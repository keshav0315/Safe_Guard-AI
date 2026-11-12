# =============================================================================
# SafeGuard AI — Production Dockerfile
# Python 3.11/3.14 compatible, multi-stage, non-root secure container
# =============================================================================

FROM python:3.11-slim as base

# Python environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/safeguard_backend:/app

WORKDIR /app

# System build dependencies install karo (Postgres client library etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pinned production requirements install karo
COPY requirements/base.txt /app/requirements/base.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements/base.txt

# Application code copy karo
COPY . /app/

# Security ke liye non-root user banao
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --no-create-home appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Expose Django Gunicorn port
EXPOSE 8000

# Gunicorn WSGI start command
CMD ["gunicorn", "--chdir", "/app/safeguard_backend", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "config.wsgi:application"]
