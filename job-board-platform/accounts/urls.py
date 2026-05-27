from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CandidateRegisterView,
    EmployerRegisterView,
    ProfileView,
)


app_name = "accounts"

urlpatterns = [
    path(
        "register/employer/",
        EmployerRegisterView.as_view(),
        name="employer-register",
    ),
    path(
        "register/candidate/",
        CandidateRegisterView.as_view(),
        name="candidate-register",
    ),
    path(
        "profile/",
        ProfileView.as_view(),
        name="profile",
    ),
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token-obtain",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# app_name sets the namespace for these routes as accounts.
#
# urlpatterns stores all account-related URL patterns.
#
# register/employer/ sends employer registration requests to
# EmployerRegisterView.
#
# register/candidate/ sends candidate registration requests to
# CandidateRegisterView.
#
# profile/ sends profile read and update requests to ProfileView.
#
# token/ uses TokenObtainPairView so users can receive JWT access and refresh
# tokens.
#
# token/refresh/ uses TokenRefreshView so clients can request a new access
# token with a valid refresh token.
#
# Important decisions that were made and why
#
# Authentication routes are placed in accounts because login tokens belong to
# user account access.
#
# The route names are descriptive so reverse("accounts:profile") and similar
# lookups are easy to understand.
#
# What you should read and understand before you review the code
#
# Read Django path and app_name namespacing.
#
# Read Django REST Framework Simple JWT token obtain and refresh views.
#
# Read how include(..., namespace="accounts") uses app_name.
#
# ============================================================
# END OF REVIEW
# ============================================================
