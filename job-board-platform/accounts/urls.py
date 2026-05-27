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


