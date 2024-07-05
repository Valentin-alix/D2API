#!/bin/bash

poetry run python scripts/populate/extern/populate_extern.py
poetry run uvicorn --workers 1 --host 0.0.0.0 main:app