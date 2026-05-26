"""
Django settings for the task3_restaurant_mgmt API project.
"""

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import Csv, config


BASE_DIR = Path(__file__).resolve().parent.parent


def cast_bool(value):
    """Return a boolean for common environment flag values."""
    true_values = {"1", "true", "yes", "on", "debug"}
    false_values = {"0", "false", "no", "off", "release", "production"}
    normalized_value = str(value).strip().lower()

    if normalized_value in true_values:
        return True

    if normalized_value in false_values:
        return False

    raise ValueError(f"Invalid boolean value: {value}")


# Core settings
SECRET_KEY = config("SECRET_KEY")
DEBUG = config(
    "DEBUG",
    default="RENDER" not in os.environ,
    cast=cast_bool,
)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=Csv(),
)
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_yasg",
    "accounts",
    "menu",
    "orders.apps.OrdersConfig",
    "reservations",
    "inventory",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
SQLITE_URL = "sqlite:///" + str(BASE_DIR / "db.sqlite3").replace("\\", "/")

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default=SQLITE_URL),
        conn_max_age=600,
    )
}


# Custom user model
AUTH_USER_MODEL = "accounts.User"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = config("TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True


# Static and media files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}


# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 20,
}


# Simple JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# CORS
CORS_ALLOW_ALL_ORIGINS = config(
    "CORS_ALLOW_ALL_ORIGINS",
    default=DEBUG,
    cast=cast_bool,
)
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="",
    cast=Csv(),
)


# Production security
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=Csv(),
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config(
    "SECURE_SSL_REDIRECT",
    default=False,
    cast=cast_bool,
)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG


# Swagger / drf-yasg
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter: Bearer <your access token>",
        },
    },
    "USE_SESSION_AUTH": False,
}

REDOC_SETTINGS = {
    "LAZY_RENDERING": False,
}


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# cast_bool converts common environment words into True or False. It is used
# for DEBUG, CORS_ALLOW_ALL_ORIGINS, and SECURE_SSL_REDIRECT.
#
# os is imported so settings can read Render-provided environment variables
# such as RENDER_EXTERNAL_HOSTNAME.
#
# Path builds file paths safely across operating systems.
#
# timedelta is used because Simple JWT expects token lifetimes as time objects.
#
# config and Csv come from python-decouple. config reads environment values,
# and Csv turns comma-separated values into Python lists.
#
# dj_database_url.config turns DATABASE_URL into Django's DATABASES format.
#
# SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL, TIME_ZONE, CORS, CSRF, and
# SSL settings are environment-driven so deployment values are not hard-coded.
#
# DEBUG defaults to True locally, but defaults to False on Render because
# Render sets the RENDER environment variable.
#
# RENDER_EXTERNAL_HOSTNAME is added to ALLOWED_HOSTS automatically so the
# Render service URL can serve requests without manual duplication.
#
# INSTALLED_APPS uses orders.apps.OrdersConfig instead of plain "orders" so
# AppConfig.ready imports orders.signals when Django starts.
#
# WhiteNoiseMiddleware is placed after SecurityMiddleware so static files can
# be served efficiently in production.
#
# STORAGES configures normal uploaded file storage and compressed manifest
# static file storage for WhiteNoise.
#
# REST_FRAMEWORK sets JWT authentication, authenticated access by default, and
# page-number pagination.
#
# SIMPLE_JWT sets access and refresh token lifetimes and uses the Bearer
# authorization header format.
#
# CORS_ALLOWED_ORIGINS and CORS_ALLOW_ALL_ORIGINS control browser access from
# frontend domains.
#
# CSRF_TRUSTED_ORIGINS allows trusted HTTPS origins to submit CSRF-protected
# requests.
#
# SECURE_PROXY_SSL_HEADER tells Django to trust Render's forwarded HTTPS
# header.
#
# Cookie and HSTS settings become strict when DEBUG is False.
#
# SWAGGER_SETTINGS tells drf_yasg that protected endpoints use a Bearer token
# in the Authorization header.
#
# Important decisions that were made and why
#
# SQLite remains the local default because it works without extra setup.
#
# DATABASE_URL enables PostgreSQL on Render without changing code.
#
# WhiteNoise is used because Render's Django guide recommends it for serving
# static files from the app service.
#
# SECURE_SSL_REDIRECT is environment-controlled so tests and local production
# checks can run without unwanted redirects, while Render can set it to True.
#
# Cookie and HSTS settings depend on DEBUG so local development stays
# convenient and production becomes stricter.
#
# The signals app config is explicit because inventory deduction and restore
# behavior depend on orders.signals being imported.
#
# What you should read and understand before you review the code
#
# Read Django settings basics, especially INSTALLED_APPS, MIDDLEWARE,
# DATABASES, AUTH_USER_MODEL, STORAGES, STATIC_URL, and MEDIA_URL.
#
# Read Django deployment security settings and the deployment checklist.
#
# Read Render environment variables, build commands, and PostgreSQL setup.
#
# Read WhiteNoise setup for Django static files.
#
# Read Django AppConfig.ready so you understand how signals are registered.
#
# ============================================================
# END OF REVIEW
# ============================================================
