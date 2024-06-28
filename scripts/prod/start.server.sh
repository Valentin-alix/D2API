#!/bin/bash

parent_path=$( cd "$(dirname $(dirname $(dirname "${BASH_SOURCE[0]}")))" ; pwd -P )
cd "$parent_path"

docker system prune --force

docker compose -f docker-compose.prod.yml down --remove-orphans

docker rmi ezred2api || true

docker compose -f docker-compose.prod.yml build --no-cache --force-rm

docker compose -f docker-compose.prod.yml up -d --force-recreate