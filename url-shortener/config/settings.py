"""
Django settings for the config project.
"""

from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import Csv, config


BASE_DIR = Path(__file__).resolve().parent.parent


def cast_bool(value):
    """Convert common environment values into a real boolean."""
    normalized_value = str(value).strip().lower()
    true_values = {"1", "true", "yes", "on"}
    false_values = {"0", "false", "no", "off", "release", "production"}

    if normalized_value in true_values:
        return True

    if normalized_value in false_values:
        return False

    raise ValueError(f"Invalid boolean value: {value}")


SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=cast_bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=Csv(),
)


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
    "shortener",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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


DATABASES = {
    "default": dj_database_url.parse(
        config(
            "DATABASE_URL",
            default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        ),
        conn_max_age=600,
    ),
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "shortener.User"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


CORS_ALLOW_ALL_ORIGINS = True


SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT format: Bearer <access_token>",
        },
    },
}

REDOC_SETTINGS = {
    "LAZY_RENDERING": False,
}


if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "shortener": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# This file is the main settings file for the Django project. Django reads
# it when the server starts, when migrations run, and when tests run.
#
# There are no custom classes in this file. Settings files usually define
# variables, not classes. Those variables tell Django and third-party apps
# how the project should behave.
#
# The imports at the top do this:
# - timedelta is used to write JWT token lifetimes in a clear way.
# - Path is used to build file paths that work on Windows, macOS, and Linux.
# - dj_database_url converts a DATABASE_URL string into Django's database
#   dictionary format.
# - Config, Csv, and RepositoryEnv come from python-decouple. They read
#   values from the .env file and convert those values into useful Python
#   types.
#
# BASE_DIR stores the root folder of the project. It is used to build paths
# for the database, templates, static files, and media files.
#
# cast_bool is a small helper function. It changes text values like True,
# False, yes, no, release, or production into real Python boolean values.
# It exists because environment variables are always text.
#
# SECRET_KEY is loaded from .env because it is private. A real production
# secret key should never be committed to GitHub.
#
# DEBUG is loaded from .env and converted to True or False. It should be
# True while developing locally and False in production.
#
# ALLOWED_HOSTS is loaded from .env as a comma-separated list. Django uses
# it to decide which domains are allowed to serve this project.
#
# INSTALLED_APPS includes Django's built-in apps and the apps needed for
# this API:
# - rest_framework provides Django REST Framework.
# - corsheaders handles cross-origin requests from a frontend.
# - drf_yasg creates Swagger and ReDoc API documentation.
# - shortener is the app that will contain the URL shortener code.
#
# MIDDLEWARE defines code that runs during every request and response.
# CorsMiddleware is placed near the top so CORS headers can be added early.
#
# ROOT_URLCONF tells Django that the main URL routes are in config.urls.
#
# TEMPLATES keeps Django template support enabled. A project-level templates
# folder is included in case templates are needed later.
#
# WSGI_APPLICATION points to the WSGI application used by many production
# servers.
#
# DATABASES uses DATABASE_URL from .env. If DATABASE_URL is missing, it uses
# SQLite by default. If DATABASE_URL contains a PostgreSQL URL, the project
# will use PostgreSQL without changing this settings file.
#
# AUTH_PASSWORD_VALIDATORS keeps Django's default password safety checks.
# These help reject weak passwords for admin and user accounts.
#
# LANGUAGE_CODE, TIME_ZONE, USE_I18N, and USE_TZ control localization and
# timezone behavior. UTC is a good default for APIs.
#
# STATIC_URL, STATIC_ROOT, and STATICFILES_DIRS configure static files like
# CSS, JavaScript, and images.
#
# MEDIA_URL and MEDIA_ROOT configure uploaded files. The URL shortener may
# not need uploads immediately, but this is a standard project setup.
#
# DEFAULT_AUTO_FIELD tells Django to use BigAutoField for automatic primary
# keys. This matches modern Django defaults.
#
# REST_FRAMEWORK sets JWT authentication as the default authentication
# method. It also enables PageNumberPagination with 20 items per page.
#
# SIMPLE_JWT sets access tokens to last 60 minutes and refresh tokens to
# last 7 days. Access tokens are shorter-lived for safety. Refresh tokens
# last longer so users do not need to log in too often.
#
# CORS_ALLOW_ALL_ORIGINS=True is useful during development because any local
# frontend can call the API. In production, replace it with a specific list
# of allowed origins.
#
# SWAGGER_SETTINGS configures drf_yasg. Session authentication is disabled
# because this API uses JWT. The Bearer security definition tells Swagger
# to send JWT tokens in the Authorization header.
#
# REDOC_SETTINGS controls ReDoc behavior for API documentation.
#
# The LOGGING block only runs when DEBUG=True. It sends logs to the console
# so errors and useful messages are visible while developing.
#
# Important decisions made:
# - Secrets and environment-specific values are stored in .env instead of
#   being hardcoded.
# - SQLite is the default database because it is simple for development.
# - PostgreSQL can be used later by changing DATABASE_URL only.
# - JWT is configured globally so protected API views can use it by default.
# - Pagination is configured globally so list endpoints behave consistently.
# - CORS is open only for development convenience.
# - Console logging is enabled only in development.
#
# Before reviewing this code, read and understand:
# - Django settings.py basics.
# - How .env files protect secrets.
# - How DATABASE_URL works for SQLite and PostgreSQL.
# - The difference between access tokens and refresh tokens in JWT.
# - How CORS affects API requests from a frontend.
# - How Swagger/OpenAPI documentation describes an API.
# - The difference between static files and media files in Django.
#
# ============================================================
# END OF REVIEW
# ============================================================
