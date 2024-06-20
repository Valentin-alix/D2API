#!/bin/bash

cat init.sql | docker exec -i ezred2api-db psql -U postgres -d ezred2db