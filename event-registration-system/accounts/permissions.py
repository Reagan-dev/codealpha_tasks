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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# IsMember checks whether the logged-in user has the MEMBER role. It is useful
# for endpoints that should be available to normal event attendees only.
#
# has_permission runs before the view action. It returns True only when the user
# is authenticated and their role is MEMBER.
#
# The message attribute gives a clear API error when access is denied.
#
# Important decisions that were made and why
#
# request.user.is_authenticated is checked first so anonymous users cannot pass
# the permission.
#
# getattr is used for role access so the permission fails safely if the user
# object does not have a role attribute.
#
# This permission uses has_permission instead of has_object_permission because
# it checks the user's role, not ownership of a specific object.
#
# What you should read and understand before you review the code
#
# Read DRF permission classes and BasePermission.
#
# Read has_permission and when it runs in the request lifecycle.
#
# Read how role-based access control works at a simple API level.
#
# ============================================================
# END OF REVIEW
# ============================================================
