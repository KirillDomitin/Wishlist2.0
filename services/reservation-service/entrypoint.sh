#!/bin/sh
export PYTHONPATH=/app

echo "Waiting for database..."
until alembic upgrade head; do
  echo "Migration failed, retrying in 3s..."
  sleep 3
done

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
