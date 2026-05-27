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


