#!/bin/bash
set -e

echo "Starting CRM API..."
echo "Working directory: $(pwd)"
echo "Python path: $(which python)"
echo "Python version: $(python --version)"

# Test database connection
echo "Testing database connection..."
python -c "
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
    python manage.py migrate --noinput || {
        echo "ERROR: Database migrations failed!"
        echo "This might be due to database connection issues."
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

