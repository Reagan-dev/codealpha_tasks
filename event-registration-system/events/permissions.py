from rest_framework.permissions import BasePermission


class IsOrganizer(BasePermission):
    """Allow access only to authenticated organizer users."""

    message = "You must be an organizer to perform this action."

    def has_permission(self, request, view):
        """Return True when the request user has the organizer role."""
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "ORGANIZER"
        )


class IsEventOrganizer(BasePermission):
    """Allow object access only to the user who organizes the event."""

    message = "You can only modify events you organize."

    def has_object_permission(self, request, view, obj):
        """Return True when the request user owns the event object."""
        return (
            request.user.is_authenticated
            and request.user == obj.organizer
        )


class IsRegistrationOwner(BasePermission):
    """Allow object access only to the user who owns the registration."""

    message = "You can only manage your own registrations."

    def has_object_permission(self, request, view, obj):
        """Return True when the request user owns the registration object."""
        return request.user.is_authenticated and request.user == obj.user


