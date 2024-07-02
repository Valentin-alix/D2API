#!/bin/bash

set -e

poetry run poetry install

git submodule init
git submodule update

docker-compose -f docker-compose.dev.yml up -d

python scripts/populate/dofus/populate_dofus.py
python scripts/populate/extern/populate_extern.py