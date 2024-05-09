#!/bin/bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

if [ -f thoughts_app_service/thoughts_app/thoughts_core/migrations/0001_initial.py ]; then
    rm thoughts_app_service/thoughts_app/thoughts_core/migrations/0001_initial.py
    echo -e "${GREEN}File thoughts_app_service/thoughts_app/thoughts_core/migrations/0001_initial.py deleted.${NC}"
else
    echo -e "${RED}File thoughts_app_service/thoughts_app/thoughts_core/migrations/0001_initial.py does not exist. Exiting...${NC}"
fi

echo -e "${GREEN}Running migrations...${NC}"
python3 thoughts_app_service/thoughts_app/manage.py makemigrations

echo -e "${GREEN}Clearing Postgres volume...${NC}"
source clear_postgres_volume.sh

echo -e "${GREEN}Starting Docker containers...${NC}"
docker-compose up --build -d