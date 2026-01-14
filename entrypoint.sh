#!/bin/sh

echo "Applying migrations"

python manage.py migrate

exec "$@"