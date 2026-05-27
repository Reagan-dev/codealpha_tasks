from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import (
    CandidateProfileSerializer,
    CandidateRegistrationSerializer,
    EmployerProfileSerializer,
    EmployerRegistrationSerializer,
)


class EmployerRegisterView(CreateAPIView):
    """Register a new employer account."""

    serializer_class = EmployerRegistrationSerializer
    permission_classes = [AllowAny]


class CandidateRegisterView(CreateAPIView):
    """Register a new candidate account."""

    serializer_class = CandidateRegistrationSerializer
    permission_classes = [AllowAny]


class ProfileView(RetrieveUpdateAPIView):
    """Return and update the authenticated user's role-specific profile."""

    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user

        if user.role == "EMPLOYER":
            return user.employer_profile

        return user.candidate_profile

    def get_serializer_class(self):
        if self.request.user.role == "EMPLOYER":
            return EmployerProfileSerializer

        return CandidateProfileSerializer


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# EmployerRegisterView creates employer accounts through the existing
# EmployerRegistrationSerializer.
#
# CandidateRegisterView creates candidate accounts through the existing
# CandidateRegistrationSerializer.
#
# ProfileView returns the profile object that belongs to the signed-in user.
#
# get_object checks the user's role and returns either employer_profile or
# candidate_profile.
#
# get_serializer_class chooses the matching profile serializer so employers
# and candidates see and update the correct fields.
#
# Important decisions that were made and why
#
# Registration views use AllowAny because new users are not authenticated yet.
#
# ProfileView uses IsAuthenticated because only logged-in users should read or
# edit their own profile.
#
# ProfileView works with the role-specific profile model instead of exposing
# every user account field through this endpoint.
#
# What you should read and understand before you review the code
#
# Read DRF CreateAPIView and RetrieveUpdateAPIView.
#
# Read permission_classes and how AllowAny and IsAuthenticated work.
#
# Read OneToOneField reverse access such as user.employer_profile.
#
# ============================================================
# END OF REVIEW
# ============================================================
