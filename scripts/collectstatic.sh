#!/bin/bash
set -e

cd /app/
echo "collecting static files"
/py/bin/python manage.py collectstatic --noinput --ignore "*.scss"
