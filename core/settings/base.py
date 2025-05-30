import os
from pathlib import Path

from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

load_dotenv()

MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "accounts",
    "base",
    "chat",
    "specialties",
    "widget_tweaks",
    "mathfilters",
    "cloudinary_storage",
    "cloudinary",
    "captcha",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.middleware.meta_tags.HreflangMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.doctor_messages",
                "chat.context_processors.get_unread_messages_count",
            ],
            "libraries": {
                "hts": "common.templatetags.hts",
            },
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
]

LANGUAGE_CODE = "ar"

TIME_ZONE = "Asia/Damascus"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

LANGUAGES = (
    ("ar", _("Arabic")),
    ("en", _("English")),
)

LOCALE_PATHS = [
    BASE_DIR / "locale/",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/accounts/login/"
AUTH_USER_MODEL = "accounts.User"

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

MEDIA_URL = "/uploads/"

SITE_ID = 1

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD"),
    "API_KEY": os.environ.get("CLOUDINARY_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_SECRET"),
    "STATIC_IMAGES_EXTENSIONS": [
        "jpg",
        "jpe",
        "jpeg",
        "jpc",
        "jp2",
        "j2k",
        "wdp",
        "jxr",
        "hdp",
        "png",
        "gif",
        "webp",
        "bmp",
        "tif",
        "tiff",
        "ico",
    ],
}

RECAPTCHA_PUBLIC_KEY = "6LfAslArAAAAABp8V_JgUWomShNL8uK5zkOLATuL"
RECAPTCHA_PRIVATE_KEY = "6LfAslArAAAAAB4_DNmUez4HRB9SyjtFCm8bxr2P"
SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]
