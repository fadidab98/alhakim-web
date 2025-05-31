# prod.py
import os

from dotenv import load_dotenv

from .base import *

load_dotenv()

ALLOWED_HOSTS = ["*"]

DEBUG = True

SECRET_KEY = os.environ.get("SECRET_KEY")

STATIC_URL = "/staticfiles/"
STATIC_ROOT = "/app/staticfiles"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DATABASE_NAME"),
        "USER": os.environ.get("DATABASE_USER"),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
        "HOST": "db",
        "PORT": "5432",
    }
}
EMAIL_HOST_USER=consultation.alhakim@gmail.com
EMAIL_HOST_PASSWORD=bmmviyhxntrcnwnd
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")bmmviyhxntrcnwnd
EMAIL_USE_TLS = True



SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
