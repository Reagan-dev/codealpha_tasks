from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    QRCodeView,
    RedirectView,
    ShortenURLView,
    URLDetailView,
    URLListView,
)


app_name = "shortener"

urlpatterns = [
    path(
        "api/shorten/",
        ShortenURLView.as_view(),
        name="shorten-url",
    ),
    path(
        "s/<str:short_code>/",
        RedirectView.as_view(),
        name="redirect-url",
    ),
    path(
        "api/links/",
        URLListView.as_view(),
        name="url-list",
    ),
    path(
        "api/links/<str:short_code>/",
        URLDetailView.as_view(),
        name="url-detail",
    ),
    path(
        "api/links/<str:short_code>/qr/",
        QRCodeView.as_view(),
        name="url-qr-code",
    ),
    path(
        "api/auth/token/",
        TokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),
    path(
        "api/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]


