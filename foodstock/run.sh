#!/usr/bin/with-contenv bashio

set -e

echo "Starting FoodStock Backend..."

DATABASE_HOST="$(bashio::config 'database_host')"
DATABASE_PORT="$(bashio::config 'database_port')"
DATABASE_NAME="$(bashio::config 'database_name')"
DATABASE_USER="$(bashio::config 'database_user')"
DATABASE_PASSWORD="$(bashio::config 'database_password')"

export DATABASE_URL="postgresql+psycopg://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}"
export JWT_SECRET="$(bashio::config 'jwt_secret')"
export INITIAL_ADMIN_USERNAME="$(bashio::config 'initial_admin_username')"
export INITIAL_ADMIN_PASSWORD="$(bashio::config 'initial_admin_password')"
export JWT_EXPIRES_HOURS="$(bashio::config 'jwt_expires_hours')"
export FOODSTOCK_DATA_DIR="/data/foodstock"

echo "Database host: ${DATABASE_HOST}"
echo "Database port: ${DATABASE_PORT}"
echo "Database name: ${DATABASE_NAME}"
echo "Database user: ${DATABASE_USER}"

exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
