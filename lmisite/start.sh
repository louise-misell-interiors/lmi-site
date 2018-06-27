#!/usr/bin/env bash

python3 manage.py collectstatic --no-input
python3 manage.py migrate
echo Starting Gunicorn.
exec gunicorn lmisite.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 5
