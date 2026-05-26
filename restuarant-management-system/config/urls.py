from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Restaurant Management System API",
        default_version="v1",
        description="API documentation for the Restaurant Management System.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "swagger.json",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path(
        "api/accounts/",
        include("accounts.urls", namespace="accounts"),
    ),
    path(
        "api/menu/",
        include("menu.urls", namespace="menu"),
    ),
    path(
        "api/",
        include("reservations.urls", namespace="reservations"),
    ),
    path(
        "api/",
        include("orders.urls", namespace="orders"),
    ),
    path(
        "api/",
        include("inventory.urls", namespace="inventory"),
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
# schema_view builds the Swagger and ReDoc schema views using drf_yasg.
#
# openapi.Info stores the API title, version, and description shown in the
# documentation pages.
#
# urlpatterns maps admin, Swagger JSON, Swagger UI, ReDoc, and every app URL
# module into the project.
#
# include() connects each app's urls.py to the main project URL tree.
#
# static() serves uploaded media files during local development when DEBUG is
# True.
#
# Important decisions that were made and why
#
# Every app is included with a namespace so URL names stay clear even when
# different apps use similar names.
#
# Swagger and ReDoc are public because developers need to read API docs before
# they authenticate.
#
# App URLs are grouped under /api/ so the API stays separate from /admin/ and
# documentation routes.
#
# What you should read and understand before you review the code
#
# Read Django include(), app_name, and namespace.
#
# Read drf_yasg get_schema_view, with_ui, and without_ui.
#
# Read why media files are served by Django only in development.
#
# ============================================================
# END OF REVIEW
# ============================================================
