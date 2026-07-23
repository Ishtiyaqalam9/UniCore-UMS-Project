#!/bin/bash
set -e

python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py migrate --database=mysql
python manage.py migrate --database=postgres
python manage.py collectstatic --noinput
python manage.py createsuperuser

echo "Setup complete. Run ./run_server_mac.sh"
