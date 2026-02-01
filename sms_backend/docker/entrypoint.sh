#!/bin/bash
# =============================================================================
# SMS Docker Entrypoint Script (Production, Role-Aware)
# =============================================================================

set -e

ROLE=${SERVICE_ROLE:-web}

echo "[INFO] Container role: ${ROLE}"

# -----------------------------------------------------------------------------
# Wait for PostgreSQL
# -----------------------------------------------------------------------------
echo "[INFO] Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "[INFO] Database is ready"

# -----------------------------------------------------------------------------
# Wait for Redis
# -----------------------------------------------------------------------------
echo "[INFO] Waiting for redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "[INFO] Redis is ready"

# -----------------------------------------------------------------------------
# WEB ROLE (Django + Gunicorn)
# -----------------------------------------------------------------------------
if [ "$ROLE" = "web" ]; then
  echo "[INFO] Running migrations..."
  python manage.py migrate --noinput

  echo "[INFO] Preparing static/media/log directories..."
  mkdir -p /app/staticfiles /app/media /app/logs
  chown -R sms:sms /app/staticfiles /app/media /app/logs || true

  echo "[INFO] Collecting static files..."
  python manage.py collectstatic --noinput

  if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "[INFO] Creating superuser if not exists..."
    python manage.py createsuperuser --noinput || true
  fi

  echo "[INFO] Starting Gunicorn..."
  exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120
fi

# -----------------------------------------------------------------------------
# CELERY WORKER ROLE
# -----------------------------------------------------------------------------
if [ "$ROLE" = "worker" ]; then
  echo "[INFO] Starting Celery worker..."
  exec celery -A config.celery worker -l info --concurrency=4
fi

# -----------------------------------------------------------------------------
# CELERY BEAT ROLE
# -----------------------------------------------------------------------------
if [ "$ROLE" = "beat" ]; then
  echo "[INFO] Starting Celery beat..."
  exec celery -A config.celery beat -l info \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
fi

# -----------------------------------------------------------------------------
# FALLBACK (should not happen)
# -----------------------------------------------------------------------------
echo "[ERROR] Unknown SERVICE_ROLE=${ROLE}"
exit 1

