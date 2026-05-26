from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


app_name = "accounts"


urlpatterns = [
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path(
        "token/verify/",
        TokenVerifyView.as_view(),
        name="token-verify",
    ),
]


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# app_name names this URL module as "accounts" for namespaced URL reversing.
#
# urlpatterns maps JWT authentication endpoints to Simple JWT's built-in
# views.
#
# TokenObtainPairView accepts user credentials and returns access and refresh
# tokens.
#
# TokenRefreshView accepts a refresh token and returns a new access token.
#
# TokenVerifyView checks whether a token is valid.
#
# Important decisions that were made and why
#
# Simple JWT built-in views are used because this project already configures
# JWT authentication in settings.py.
#
# These endpoints live under accounts because authentication belongs to user
# account access.
#
# What you should read and understand before you review the code
#
# Read Simple JWT token obtain, refresh, and verify views.
#
# Read how DRF JWT authentication uses the Authorization: Bearer header.
#
# ============================================================
# END OF REVIEW
# ============================================================
