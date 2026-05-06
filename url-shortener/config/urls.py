from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="URL Shortener API",
        default_version="v1",
        description=(
            "A professional URL shortening service with analytics and "
            "QR codes"
        ),
        contact=openapi.Contact(email="support@example.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", include("shortener.urls")),
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
    path("admin/", admin.site.urls),
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
# This file is the main URL configuration for the Django project. Django
# reads it to decide which view should handle each incoming request path.
#
# schema_view is created by drf_yasg's get_schema_view function. It builds
# the OpenAPI schema that powers the Swagger and ReDoc documentation pages.
#
# openapi.Info stores the public API documentation details. The title is the
# API name, default_version is v1, and the description explains what the API
# does. The contact email gives API users a place to ask for help.
#
# public=True allows the schema to be visible publicly. permission_classes
# is set to AllowAny so visitors can open the documentation without logging
# in.
#
# urlpatterns is the list of main project routes.
#
# path("", include("shortener.urls")) includes every route from the
# shortener app. This keeps app-specific routes inside shortener/urls.py and
# keeps the project URL file small.
#
# path("swagger/", ...) serves the Swagger UI. Swagger is useful for trying
# API endpoints directly in the browser.
#
# path("redoc/", ...) serves ReDoc. ReDoc is useful for reading clean API
# documentation.
#
# path("admin/", admin.site.urls) serves the Django admin panel.
#
# The final if settings.DEBUG block serves uploaded media files during local
# development. Django does not serve media files automatically in production,
# so this helper should only run while DEBUG=True.
#
# Important decisions made:
# - The shortener app URL routes are included at the project root so paths
#   like /api/shorten/ and /s/<short_code>/ match exactly.
# - Swagger and ReDoc are both enabled because Swagger is good for testing
#   requests and ReDoc is good for reading documentation.
# - The schema is public because API documentation is usually helpful during
#   development and internship review.
# - Media serving is limited to development for safety and performance.
#
# Before reviewing this code, read and understand:
# - How Django's include() function connects app URLs to project URLs.
# - How drf_yasg creates Swagger and ReDoc documentation.
# - What an OpenAPI schema is.
# - How Django admin URLs are connected.
# - Why static() media serving should only be used in development.
#
# ============================================================
# END OF REVIEW
# ============================================================
