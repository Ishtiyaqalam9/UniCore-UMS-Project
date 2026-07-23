#!/bin/bash
set -e
source venv/bin/activate
export DJANGO_DEBUG=1
python manage.py runserver --insecure
