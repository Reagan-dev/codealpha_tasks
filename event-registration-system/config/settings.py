"""
Django settings for the task2_event_registration API project.
"""

from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import Csv, config


BASE_DIR = Path(__file__).resolve().parent.parent


# Core settings
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=Csv(),
)


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
    "events",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
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
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static and media files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


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
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}


# Simple JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# CORS
CORS_ALLOW_ALL_ORIGINS = True


# Email
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


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
    "LOGIN_URL": None,
    "LOGOUT_URL": None,
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
# There are no custom classes or custom functions in this settings file.
# A Django settings file is mostly made of variables that Django and installed
# packages read when the server starts.
#
# Path from pathlib builds file paths safely on Windows, macOS, and Linux.
# timedelta is used because Simple JWT expects token lifetimes as time objects.
# config and Csv come from python-decouple. config reads values from .env, and
# Csv turns comma-separated text like "localhost,127.0.0.1" into a Python list.
# dj_database_url.config turns DATABASE_URL into Django's DATABASES format.
#
# SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL, EMAIL_HOST_USER, and
# EMAIL_HOST_PASSWORD are read from environment variables so secret or
# environment-specific values are not hard-coded into the project.
#
# INSTALLED_APPS registers Django's built-in apps, Django REST Framework,
# corsheaders, drf_yasg, and the local accounts and events apps so Django can
# find models, serializers, migrations, admin code, and API tools.
#
# MIDDLEWARE lists request/response processing layers. CorsMiddleware is near
# the top so CORS headers are added before Django returns a response.
#
# REST_FRAMEWORK sets JWT authentication as the default, requires authenticated
# users by default, enables page-number pagination, returns 20 items per page,
# and uses DRF's standard exception handler for clean API error responses.
#
# SIMPLE_JWT sets access tokens to expire after 60 minutes and refresh tokens
# after 7 days. The Authorization header must use the Bearer token format.
#
# DATABASES uses SQLite when DATABASE_URL is missing and PostgreSQL or another
# supported database when DATABASE_URL is provided.
#
# EMAIL_BACKEND uses the console backend while DEBUG is True so development
# emails print in the terminal. When DEBUG is False, it uses Gmail SMTP.
#
# SWAGGER_SETTINGS tells drf_yasg that protected endpoints use a Bearer token
# in the Authorization header and disables session login in the API docs.
#
# AUTH_USER_MODEL points Django to accounts.User, which is important because a
# custom user model must be configured before the first migrations are created.
#
# STATIC_URL, STATIC_ROOT, STATICFILES_DIRS, MEDIA_URL, and MEDIA_ROOT configure
# static files such as CSS or JavaScript and uploaded media files.
#
# Important decisions that were made and why
#
# DEBUG defaults to True because this is a development project, but production
# should set DEBUG=False in .env.
#
# CORS_ALLOW_ALL_ORIGINS is True because the requirement says to allow all
# origins during development. In production, this should be replaced with a
# strict CORS_ALLOWED_ORIGINS list.
#
# DEFAULT_PERMISSION_CLASSES uses IsAuthenticated so endpoints are protected by
# default. Public endpoints, such as registration or login, can override this in
# their views.
#
# SQLite is the default database because it works locally without extra setup.
# DATABASE_URL allows switching to PostgreSQL in production without changing
# this file.
#
# The review section is written as comments so this file remains valid Python
# until you delete the review.
#
# What you should read and understand before you review the code
#
# Read Django settings basics, especially INSTALLED_APPS, MIDDLEWARE,
# DATABASES, AUTH_USER_MODEL, STATIC_URL, and MEDIA_URL.
#
# Read Django REST Framework authentication, permissions, pagination, and
# exception handling.
#
# Read Simple JWT's access token, refresh token, and Authorization header flow.
#
# Read python-decouple and dj-database-url basics so you understand how values
# move from .env into Django.
#
# Read drf_yasg's SECURITY_DEFINITIONS setting so Swagger can send JWT tokens
# when testing protected endpoints.
#
# ============================================================
# END OF REVIEW
# ============================================================
