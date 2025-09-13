#!/usr/bin/env bash
set -e
python create_tables.py
python seed_questions.py
exec gunicorn run:app
