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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# RegisterView handles POST /api/auth/register/. It uses CreateAPIView because
# registration creates one new User object.
#
# RegisterView uses AllowAny because people must be able to create an account
# before they are logged in.
#
# perform_create saves the serializer and then sends the welcome email. This is
# the correct hook because DRF calls it after validation and before returning
# the create response.
#
# ProfileView handles GET and PATCH /api/auth/profile/. It uses
# RetrieveUpdateAPIView because the logged-in user can view and update one
# profile object.
#
# ProfileView uses IsAuthenticated because only logged-in users should access
# their own profile.
#
# get_object returns request.user so the endpoint always works with the current
# user's profile instead of requiring a user ID in the URL.
#
# Important decisions that were made and why
#
# Email sending is kept in perform_create instead of the serializer so the
# serializer stays focused on validation and object creation.
#
# The profile endpoint does not accept a pk because users should not be able to
# choose another user's profile through the URL.
#
# What you should read and understand before you review the code
#
# Read DRF generic views, especially CreateAPIView and RetrieveUpdateAPIView.
#
# Read DRF permission classes: AllowAny and IsAuthenticated.
#
# Read perform_create and get_object hooks.
#
# ============================================================
# END OF REVIEW
# ============================================================
