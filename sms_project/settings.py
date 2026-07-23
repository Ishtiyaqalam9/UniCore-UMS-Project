"""Django settings for the University Management System."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-32_-tu7rmagef74#xmoxfj)e3s7(mmi&+^of+=7oyk2o)p4i1^",
)
DEBUG = False
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "unicore-ums-project-production.up.railway.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://unicore-ums-project-production.up.railway.app",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "home",
    "student",
    "teacher",
    "library",
    "academic",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sms_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.role_context",
            ],
        },
    },
]

WSGI_APPLICATION = "sms_project.wsgi.application"

# The existing database architecture is preserved:
#   student app -> MySQL
#   teacher app -> PostgreSQL
#   Django/core/academic apps -> SQLite
# MongoDB is configured separately in library/mongo.py.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "mysql": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DATABASE", "student"),
        "USER": os.getenv("MYSQL_USER", "root"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", "Ishtiyaq@826735"),
        "HOST": os.getenv("MYSQL_HOST", "localhost"),
        "PORT": os.getenv("MYSQL_PORT", "3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    },
    "postgres": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DATABASE", "teacher"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "Ishtiyaq@826735"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    },
}

# Safe local test mode. The normal project still uses MySQL/PostgreSQL.
if os.getenv("UMS_USE_SQLITE_FOR_ALL") == "1":
    DATABASES["mysql"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / ".test_student.sqlite3",
    }
    DATABASES["postgres"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / ".test_teacher.sqlite3",
    }

DATABASE_ROUTERS = ["sms_project.db_router.DatabaseRouter"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "Asia/Dhaka")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "portal_redirect"
LOGOUT_REDIRECT_URL = "login"
