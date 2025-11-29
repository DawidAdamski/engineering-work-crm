#!/bin/bash
set -e

echo "Starting CRM API..."
echo "Working directory: $(pwd)"

# Find Python executable (try python, python3, or python3.12)
PYTHON_CMD=""
for cmd in python python3 python3.12; do
    if command -v $cmd >/dev/null 2>&1; then
        PYTHON_CMD=$cmd
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: Python not found in PATH!"
    exit 1
fi

echo "Python command: $PYTHON_CMD"
echo "Python path: $(command -v $PYTHON_CMD)"
echo "Python version: $($PYTHON_CMD --version)"

# Test database connection
echo "Testing database connection..."
$PYTHON_CMD -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'minicrm.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
print('Database connection successful!')
" || {
    echo "WARNING: Database connection test failed, but continuing..."
}

# Run database migrations if not disabled
if [ -z "$DISABLE_MIGRATE" ]; then
    echo "Running database migrations..."
    $PYTHON_CMD manage.py migrate --noinput || {
        echo "ERROR: Database migrations failed!"
        echo "This might be due to database connection issues."
        echo "Database config:"
        echo "  POSTGRES_HOST=${POSTGRES_HOST:-not set}"
        echo "  POSTGRES_DB=${POSTGRES_DB:-not set}"
        echo "  POSTGRES_USER=${POSTGRES_USER:-not set}"
        exit 1
    }
    echo "Migrations completed successfully!"
else
    echo "Skipping database migrations (DISABLE_MIGRATE is set)"
fi

# Start Gunicorn
echo "Starting Gunicorn with module: ${APP_MODULE:-minicrm.wsgi:application}"
exec gunicorn \
    --bind 0.0.0.0:8080 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance \
    ${APP_MODULE:-minicrm.wsgi:application}

