#!/usr/bin/with-contenv bashio

set -e

echo "Starting FoodStock Backend..."

exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
