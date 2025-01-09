#!/bin/bash

set -e
set -o pipefail

handle_error() {
    echo "An error occurred. Exiting..."
    exit 1
}

trap 'handle_error' ERR

migrate_database() {
    echo "Starting database migrations..."
    python manage.py makemigrations
    python manage.py migrate
}

collect_static() {
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
}

start_django_service() {
    echo "Starting Django Uvicorn service..."
    uvicorn backend.asgi:application --workers 4 --reload --host 0.0.0.0 --port 80 --env-file .env &
    uvicorn_pid=$!
}

main() {
    migrate_database
    wait

    collect_static
    wait

    start_django_service

    wait $uvicorn_pid

    echo "All services have been started."
}

main
