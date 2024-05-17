#!/bin/sh
set -e

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Run Django database migrations
echo "${GREEN}Running Django database migrations...${NC}"
python ./thoughts_app/manage.py migrate

# Wait for PostgreSQL to be ready
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "${YELLOW}Postgres is unavailable - sleeping${NC}"
  sleep 1
done

# Check if the table is empty and insert data if it is
echo "${GREEN}Checking if the table is empty and inserting data...${NC}"
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" --set ON_ERROR_STOP=1 -f init.sql

# Start the Django development server
echo "${GREEN}Starting the Django development server...${NC}"
python ./thoughts_app/manage.py runserver 0.0.0.0:8000
