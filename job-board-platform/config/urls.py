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


