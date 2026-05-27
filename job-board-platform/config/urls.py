from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Job Board Platform API",
        default_version="v1",
        description="API documentation for the Job Board Platform.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/accounts/",
        include(("accounts.urls", "accounts"), namespace="accounts"),
    ),
    path(
        "api/jobs/",
        include(("jobs.urls", "jobs"), namespace="jobs"),
    ),
    path(
        "api/applications/",
        include(
            ("applications.urls", "applications"),
            namespace="applications",
        ),
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
# schema_view builds the Swagger and ReDoc documentation views with drf_yasg.
#
# openapi.Info stores the API title, version, and short description shown in
# the documentation pages.
#
# urlpatterns stores the project's top-level URL routes.
#
# admin/ opens the Django admin site.
#
# api/accounts/ includes all account routes under the accounts namespace.
#
# api/jobs/ includes all job routes under the jobs namespace.
#
# api/applications/ includes all application routes under the applications
# namespace.
#
# swagger/ opens the interactive Swagger UI documentation.
#
# redoc/ opens the ReDoc documentation page.
#
# The DEBUG block serves uploaded media files during local development.
#
# Important decisions that were made and why
#
# Each app is included with a namespace so reverse lookups stay clear, such as
# reverse("jobs:job-list").
#
# API routes are grouped under /api/ so admin and documentation routes stay
# separate from application endpoints.
#
# Swagger and ReDoc use AllowAny because API documentation should be reachable
# during development without a token.
#
# Media serving is limited to DEBUG because production should serve media
# through a real web server or storage service.
#
# What you should read and understand before you review the code
#
# Read Django include and URL namespacing.
#
# Read drf_yasg get_schema_view, Swagger UI, and ReDoc.
#
# Read Django admin URLs and development media serving with static().
#
# ============================================================
# END OF REVIEW
# ============================================================
