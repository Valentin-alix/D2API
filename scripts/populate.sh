#!/bin/bash

cat init.sql | docker exec -i ezred2db psql -U postgres -d ezred2db