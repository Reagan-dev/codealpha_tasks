from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserProfileSerializer, UserRegistrationSerializer
from .utils import send_welcome_email


class RegisterView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        """Create a user account and send a welcome email."""
        user = serializer.save()
        send_welcome_email(user)


class ProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """Return the authenticated user as the profile object."""
        return self.request.user


