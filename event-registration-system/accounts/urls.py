from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import ProfileView, RegisterView


app_name = "accounts"

urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "profile/",
        ProfileView.as_view(),
        name="profile",
    ),
]


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# This file does not define custom classes or functions. It defines URL
# patterns that connect account API paths to account views.
#
# RegisterView is connected to /api/auth/register/ so new users can create
# accounts.
#
# TokenObtainPairView is connected to /api/auth/login/ so users can exchange
# email and password for JWT access and refresh tokens.
#
# TokenRefreshView is connected to /api/auth/token/refresh/ so clients can get a
# new access token using a valid refresh token.
#
# ProfileView is connected to /api/auth/profile/ so logged-in users can view and
# update their own profile.
#
# Important decisions that were made and why
#
# app_name = "accounts" gives these routes a namespace. That helps avoid name
# conflicts when the project grows.
#
# Every path has a name so views, tests, and templates can reverse URLs without
# hard-coding strings.
#
# Simple JWT views are placed in accounts URLs because authentication belongs to
# the account area of the API.
#
# What you should read and understand before you review the code
#
# Read Django path() and include().
#
# Read URL names and app namespaces.
#
# Read Simple JWT token obtain and token refresh endpoints.
#
# ============================================================
# END OF REVIEW
# ============================================================
