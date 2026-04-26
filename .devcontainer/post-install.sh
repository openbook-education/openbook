#! /bin/sh
npm install
poetry install --with dev,docs
poetry run src/manage.py migrate
