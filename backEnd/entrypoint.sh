#!/bin/sh
set -e

echo "Running Alembic migrations..."
alembic -c /app/alembic.ini upgrade head

echo "Starting server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
