#!/bin/sh

echo "Appling migrations"

python manage.py migrate

exec "$@"