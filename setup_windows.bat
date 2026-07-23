@echo off
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py migrate --database=mysql
python manage.py migrate --database=postgres
python manage.py collectstatic --noinput
python manage.py createsuperuser
pause
