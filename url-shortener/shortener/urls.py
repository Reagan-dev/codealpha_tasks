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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# This file defines the URL routes for the shortener app. A URL route tells
# Django which view should handle a matching request path.
#
# app_name = "shortener" gives this app a namespace. Namespacing helps when
# reversing URLs, especially if a project later has more than one app with
# similar route names.
#
# urlpatterns is the list of routes Django reads. Each path() connects a URL
# pattern to a view.
#
# The api/shorten/ route connects to ShortenURLView. It handles POST
# requests that create new short URLs.
#
# The s/<str:short_code>/ route connects to RedirectView. The <str:short_code>
# part captures the short code from the URL and passes it to the view.
#
# The api/links/ route connects to URLListView. It handles authenticated
# requests to list the current user's links.
#
# The api/links/<str:short_code>/ route connects to URLDetailView. That view
# handles both GET and DELETE because RetrieveDestroyAPIView supports both
# actions.
#
# The api/links/<str:short_code>/qr/ route connects to QRCodeView. It
# returns a PNG QR code image for the selected short link.
#
# The api/auth/token/ route connects to TokenObtainPairView from Simple JWT.
# It accepts user credentials and returns access and refresh tokens.
#
# The api/auth/token/refresh/ route connects to TokenRefreshView from Simple
# JWT. It accepts a refresh token and returns a new access token.
#
# Descriptive name values are included on every route. These names make it
# possible to reverse URLs in tests, serializers, templates, and other code
# without hardcoding the full path.
#
# Important decisions made:
# - path() is used for every route because these URLs do not need regular
#   expressions.
# - API routes are grouped under api/ to keep them separate from redirect
#   routes.
# - Redirect URLs use /s/<short_code>/ so public short links are short and
#   easy to recognize.
# - JWT routes live beside the app API routes because authentication is part
#   of using this API.
# - URLDetailView is listed once because the same route handles GET and
#   DELETE based on the HTTP method.
#
# Before reviewing this code, read and understand:
# - How Django path() routes work.
# - How path converters like <str:short_code> pass values to views.
# - How app_name creates a URL namespace.
# - How DRF class-based views choose behavior from HTTP methods.
# - How Simple JWT token and refresh endpoints work.
# - Why route names are useful for reverse URL lookup.
#
# ============================================================
# END OF REVIEW
# ============================================================
