#!/bin/sh

# Run Django database migrations
python ./thoughts_app/manage.py migrate

# Wait for PostgreSQL to be ready
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Check if the table is empty and insert data if it is
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f init.sql

# Start the Django development server
python ./thoughts_app/manage.py runserver 0.0.0.0:8000
