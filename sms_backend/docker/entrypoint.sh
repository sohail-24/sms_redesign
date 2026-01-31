#!/bin/bash
# =============================================================================
# SMS Docker Entrypoint Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Wait for database
wait_for_db() {
    log_info "Waiting for database..."
    
    until python -c "
import psycopg2
import sys
try:
    conn = psycopg2.connect(
        dbname='${DB_NAME}',
        user='${DB_USER}',
        password='${DB_PASSWORD}',
        host='${DB_HOST}',
        port='${DB_PORT}'
    )
    conn.close()
    sys.exit(0)
except psycopg2.OperationalError:
    sys.exit(1)
" 2>/dev/null; do
        log_warn "Database is unavailable - sleeping"
        sleep 1
    done
    
    log_info "Database is ready!"
}

# Wait for Redis
wait_for_redis() {
    log_info "Waiting for Redis..."
    
    until python -c "
import redis
import sys
try:
    r = redis.from_url('${REDIS_URL}')
    r.ping()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null; do
        log_warn "Redis is unavailable - sleeping"
        sleep 1
    done
    
    log_info "Redis is ready!"
}

# Run migrations
run_migrations() {
    log_info "Running database migrations..."
    python manage.py migrate --noinput
}

# Collect static files
collect_static() {
    log_info "Collecting static files..."
    python manage.py collectstatic --noinput --clear
}

# Create superuser if needed
create_superuser() {
    if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
        log_info "Creating superuser..."
        python manage.py createsuperuser --noinput 2>/dev/null || log_warn "Superuser already exists"
    fi
}

# Load initial data
load_initial_data() {
    if [ "$LOAD_INITIAL_DATA" = "true" ]; then
        log_info "Loading initial data..."
        python manage.py loaddata fixtures/initial_data.json 2>/dev/null || log_warn "No initial data found"
    fi
}

# Main execution
main() {
    log_info "Starting SMS application..."
    
    # Wait for dependencies
    wait_for_db
    wait_for_redis
    
    # Run setup tasks
    run_migrations
    collect_static
    create_superuser
    load_initial_data
    
    log_info "Setup complete! Starting application..."
    
    # Execute the passed command
    exec "$@"
}

# Run main function
main "$@"
