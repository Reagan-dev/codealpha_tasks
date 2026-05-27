"""
Django settings for the task4_job_board API project.
"""

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
DEBUG = config("DEBUG", default=True, cast=cast_bool)
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
    "jobs",
    "applications",
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
TIME_ZONE = config("TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True


# Static and media files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

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


# Email
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=cast_bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=EMAIL_HOST_USER,
)


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
# There are no custom classes in this settings file. The cast_bool function
# converts common environment words into True or False so flags like DEBUG,
# CORS_ALLOW_ALL_ORIGINS, and EMAIL_USE_TLS can be read safely from .env.
#
# Path builds file paths safely on Windows, macOS, and Linux.
#
# timedelta is used because Simple JWT expects token lifetimes as time objects.
#
# config and Csv come from python-decouple. config reads environment values,
# and Csv turns comma-separated values into Python lists.
#
# dj_database_url.config turns DATABASE_URL into Django's DATABASES format.
#
# SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL, TIME_ZONE, CORS settings, and
# email settings are read from environment variables so deployment values do
# not need to be hard-coded.
#
# INSTALLED_APPS registers Django's built-in apps, Django REST Framework,
# corsheaders, drf_yasg, and the local accounts, jobs, and applications apps.
#
# MIDDLEWARE includes CorsMiddleware near the top so CORS headers can be added
# before Django returns responses.
#
# DATABASES uses SQLite when DATABASE_URL is missing and can switch to
# PostgreSQL or another supported database when DATABASE_URL is provided.
#
# AUTH_USER_MODEL points Django to accounts.User so the project can use a
# custom user model for job seekers, employers, and admins.
#
# MEDIA_URL and MEDIA_ROOT configure uploaded files such as applicant resumes.
#
# FILE_UPLOAD_MAX_MEMORY_SIZE limits in-memory uploads to 5 MB.
#
# REST_FRAMEWORK sets JWT authentication, authenticated access by default,
# page-number pagination, and a page size of 20 records.
#
# SIMPLE_JWT sets access tokens to expire after 60 minutes and refresh tokens
# after 7 days.
#
# Email settings are environment-driven so password reset emails, application
# notifications, or employer messages can use different providers per
# environment.
#
# SWAGGER_SETTINGS tells drf_yasg that protected endpoints use a Bearer token
# in the Authorization header.
#
# Important decisions that were made and why
#
# DEBUG defaults to True because this is a development internship project.
# Production should set DEBUG=False in the environment.
#
# CORS_ALLOW_ALL_ORIGINS defaults to DEBUG. This allows all frontend origins
# during local development and can be locked down in production.
#
# SQLite is the default database because it works locally without extra setup.
# DATABASE_URL keeps production database configuration flexible.
#
# DEFAULT_PERMISSION_CLASSES uses IsAuthenticated so endpoints are protected by
# default. Public endpoints, such as job listings, can override this in views.
#
# What you should read and understand before you review the code
#
# Read Django settings basics, especially INSTALLED_APPS, MIDDLEWARE,
# DATABASES, AUTH_USER_MODEL, STATIC_URL, and MEDIA_URL.
#
# Read Django REST Framework authentication, permissions, and pagination.
#
# Read Simple JWT access token, refresh token, and Bearer header flow.
#
# Read python-decouple and dj-database-url basics.
#
# Read Django email settings and file upload settings.
#
# ============================================================
# END OF REVIEW
# ============================================================
