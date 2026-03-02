#!/usr/bin/env sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

gunicorn kallan.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${WEB_CONCURRENCY:-3} \
  --timeout 60
