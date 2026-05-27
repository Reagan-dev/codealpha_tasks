"""
Django settings for the task4_job_board API project.
"""

import os
import sys
from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import Csv, config


BASE_DIR = Path(__file__).resolve().parent.parent
IS_TESTING = "test" in sys.argv


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
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME:
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
    "jobs",
    "applications",
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
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=Csv(),
)

if RENDER_EXTERNAL_HOSTNAME:
    render_origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"

    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)


# Production security
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config(
    "SECURE_SSL_REDIRECT",
    default=not DEBUG and not IS_TESTING,
    cast=cast_bool,
)
SESSION_COOKIE_SECURE = not DEBUG and not IS_TESTING
CSRF_COOKIE_SECURE = not DEBUG and not IS_TESTING
SECURE_HSTS_SECONDS = config(
    "SECURE_HSTS_SECONDS",
    default=0 if DEBUG or IS_TESTING else 31536000,
    cast=int,
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG and not IS_TESTING
SECURE_HSTS_PRELOAD = not DEBUG and not IS_TESTING
X_FRAME_OPTIONS = "DENY"


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
# converts common environment words into True or False so settings can be read
# safely from environment variables.
#
# os reads RENDER_EXTERNAL_HOSTNAME, which Render sets automatically for the
# deployed service.
#
# sys is used to detect manage.py test so production HTTPS redirects do not
# interfere with API tests.
#
# Path builds file paths safely on Windows, macOS, and Linux.
#
# config and Csv come from python-decouple. config reads environment values,
# and Csv turns comma-separated values into Python lists.
#
# dj_database_url.config turns DATABASE_URL into Django's DATABASES format.
#
# ALLOWED_HOSTS is loaded from the environment and also includes Render's
# external hostname when Render provides it.
#
# MIDDLEWARE includes WhiteNoise after SecurityMiddleware so collected static
# files can be served in production.
#
# STORAGES uses WhiteNoise's compressed manifest storage for static files and
# Django's normal filesystem storage for uploaded media.
#
# DATABASES uses SQLite locally and switches to PostgreSQL or another database
# when DATABASE_URL is provided.
#
# CSRF_TRUSTED_ORIGINS is environment-driven and automatically includes the
# Render service origin when RENDER_EXTERNAL_HOSTNAME is available.
#
# SECURE_PROXY_SSL_HEADER tells Django to trust Render's forwarded HTTPS
# header.
#
# SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, HSTS, and
# X_FRAME_OPTIONS harden production browser security.
#
# IS_TESTING keeps those HTTPS redirects and secure-cookie defaults from
# breaking local automated tests.
#
# REST_FRAMEWORK sets JWT authentication, authenticated access by default,
# page-number pagination, and a page size of 20 records.
#
# SIMPLE_JWT sets access tokens to expire after 60 minutes and refresh tokens
# after 7 days.
#
# Email settings are environment-driven so each deployment can use its own
# SMTP provider.
#
# SWAGGER_SETTINGS tells drf_yasg that protected endpoints use a Bearer token
# in the Authorization header.
#
# Important decisions that were made and why
#
# DEBUG defaults to True for local development, but production should set
# DEBUG=False.
#
# CORS_ALLOW_ALL_ORIGINS defaults to DEBUG so local frontend development is
# easy and production can be locked down to known origins.
#
# SQLite is the fallback database because it works locally without setup.
# Render production should use DATABASE_URL from a managed PostgreSQL service.
#
# WhiteNoise is used for static files because Render runs the Django app
# directly behind Gunicorn and does not automatically serve collected static
# files for Django.
#
# Media files still use local filesystem storage by default because Cloudinary
# or S3 credentials are project-specific and should be added intentionally.
#
# What you should read and understand before you review the code
#
# Read Django settings basics, especially INSTALLED_APPS, MIDDLEWARE,
# DATABASES, AUTH_USER_MODEL, STATIC_URL, MEDIA_URL, and STORAGES.
#
# Read Django deployment security settings and the deployment checklist.
#
# Read WhiteNoise static file serving for Django.
#
# Read Render's Django deployment guide.
#
# Read Django REST Framework authentication, permissions, and pagination.
#
# Read Simple JWT access token, refresh token, and Bearer header flow.
#
# Read python-decouple and dj-database-url basics.
#
# ============================================================
# END OF REVIEW
# ============================================================
