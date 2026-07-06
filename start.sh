#!/bin/sh

echo "Waiting for PostgreSQL..."

sleep 10

echo "Starting FastAPI..."

uvicorn app.main:app --host 0.0.0.0 --port 8000