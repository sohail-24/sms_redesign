#!/bin/bash
set -e

ROLE=${SERVICE_ROLE:-web}

echo "[INFO] Container role: ${ROLE}"

# ------------------------------------------------------------------
# Wait for PostgreSQL
# ------------------------------------------------------------------
until python - <<EOF
import psycopg2, os
try:
    psycopg2.connect(
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
    )
    exit(0)
except Exception:
    exit(1)
EOF
do
  echo "[INFO] Waiting for PostgreSQL..."
  sleep 2
done

# ------------------------------------------------------------------
# Wait for Redis
# ------------------------------------------------------------------
until python - <<EOF
import redis, os
try:
    redis.from_url(os.environ.get("REDIS_URL")).ping()
    exit(0)
except Exception:
    exit(1)
EOF
do
  echo "[INFO] Waiting for Redis..."
  sleep 2
done

# ================================================================
# WEB ROLE
# ================================================================
if [ "$ROLE" = "web" ]; then
  echo "[INFO] Running migrations..."
  python manage.py migrate --noinput

  echo "[INFO] Collecting static files..."
  python manage.py collectstatic --noinput || true


  echo "[INFO] Starting Gunicorn..."
  exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120
fi

# ================================================================
# CELERY WORKER ROLE
# ================================================================
if [ "$ROLE" = "worker" ]; then
  echo "[INFO] Starting Celery worker..."
  exec celery -A infrastructure.celery.celery_app worker -l info
fi

# ================================================================
# CELERY BEAT ROLE
# ================================================================
if [ "$ROLE" = "beat" ]; then
  echo "[INFO] Running django_celery_beat migrations..."
  python manage.py migrate django_celery_beat --noinput

  echo "[INFO] Starting Celery beat..."
  exec celery -A infrastructure.celery.celery_app beat -l info \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
fi



echo "[ERROR] Unknown SERVICE_ROLE=${ROLE}"
exit 1

