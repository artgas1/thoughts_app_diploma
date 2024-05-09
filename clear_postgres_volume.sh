#!/bin/bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Stopping the Docker containers...${NC}"
docker-compose down

echo -e "${GREEN}Removing the PostgreSQL data volume...${NC}"
docker volume rm $(docker volume ls -qf "name=thoughtsapp_postgres_data")

echo -e "${GREEN}Script execution completed.${NC}"