#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."

python manage.py migrate --noinput

echo "Collecting static files..."

python manage.py collectstatic --noinput

echo "Creating demo data..."

python manage.py seed_data

echo "Starting Django development server..."

exec python manage.py runserver 0.0.0.0:8000