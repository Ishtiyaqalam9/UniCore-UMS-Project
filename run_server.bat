@echo off
call venv\Scripts\activate
set DJANGO_DEBUG=1
python manage.py runserver --insecure
pause
