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


