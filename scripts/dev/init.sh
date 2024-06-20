#!/bin/bash

set -e

poetry run poetry install

git submodule init
git submodule update