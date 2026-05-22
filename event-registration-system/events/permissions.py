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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# IsOrganizer checks general access before a view action runs. It allows the
# request only when the user is authenticated and has role equal to ORGANIZER.
#
# IsEventOrganizer checks object-level access for Event objects. It allows the
# request only when the logged-in user is the same user saved as obj.organizer.
#
# IsRegistrationOwner checks object-level access for Registration objects. It
# allows the request only when the logged-in user is the same user saved as
# obj.user.
#
# Each class has a message attribute. DRF uses that message when permission is
# denied, which gives the client a clear explanation.
#
# Important decisions that were made and why
#
# request.user.is_authenticated is checked before role or ownership checks so
# anonymous users are rejected safely.
#
# getattr is used in IsOrganizer so the permission does not crash if the user
# object does not have a role attribute.
#
# IsOrganizer is for view-level rules. IsEventOrganizer and IsRegistrationOwner
# are for object-level rules because they need a specific Event or Registration
# object to compare against.
#
# What you should read and understand before you review the code
#
# Read DRF permission classes and BasePermission.
#
# Read the difference between has_permission and has_object_permission.
#
# Read how DRF uses the message attribute when a permission check fails.
#
# ============================================================
# END OF REVIEW
# ============================================================
