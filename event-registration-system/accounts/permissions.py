from rest_framework.permissions import BasePermission


class IsMember(BasePermission):
    """Allow access only to authenticated member users."""

    message = "You must be a member to perform this action."

    def has_permission(self, request, view):
        """Return True when the request user has the member role."""
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "MEMBER"
        )



