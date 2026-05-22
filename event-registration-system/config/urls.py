from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Event Registration System API",
        default_version="v1",
        description="API documentation for the Event Registration System.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
        name="admin",
    ),
    path(
        "api/auth/",
        include("accounts.urls"),
        name="accounts_urls",
    ),
    path(
        "api/",
        include("events.urls"),
        name="events_urls",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="swagger",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# This file does not define custom classes or functions. It defines the main
# project URL patterns and the Swagger schema view.
#
# schema_view is created with drf_yasg's get_schema_view. It tells drf_yasg the
# API title, version, description, and permission rule for the documentation.
#
# /admin/ points to the Django admin site.
#
# /api/auth/ includes all account and JWT routes from accounts.urls.
#
# /api/ includes all category, event, and registration routes from events.urls.
#
# /swagger/ shows interactive Swagger API documentation.
#
# /redoc/ shows ReDoc API documentation.
#
# The static() helper serves uploaded media files during development when
# DEBUG=True.
#
# Important decisions that were made and why
#
# path() is used for every route because the project does not need regex URL
# patterns.
#
# Account URLs are grouped under /api/auth/ because they handle registration,
# login, token refresh, and profile actions.
#
# Event URLs are grouped under /api/ so endpoints match simple paths like
# /api/events/ and /api/registrations/.
#
# Swagger and ReDoc are public because API documentation should be easy to open
# during development.
#
# What you should read and understand before you review the code
#
# Read Django include() so you understand how app URL files are connected to the
# project URL file.
#
# Read drf_yasg get_schema_view, Swagger UI, and ReDoc UI.
#
# Read Django's development media serving with django.conf.urls.static.static.
#
# ============================================================
# END OF REVIEW
# ============================================================
