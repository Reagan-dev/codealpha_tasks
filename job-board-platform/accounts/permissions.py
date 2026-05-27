from rest_framework.permissions import BasePermission


class IsEmployer(BasePermission):
    """Allow access only to authenticated employer users."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "EMPLOYER"
        )


class IsCandidate(BasePermission):
    """Allow access only to authenticated candidate users."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "CANDIDATE"
        )


class IsJobOwner(BasePermission):
    """Allow object access only to the employer who owns the job."""

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and obj.employer == request.user
        )


class IsApplicationOwner(BasePermission):
    """Allow object access only to the candidate who owns the application."""

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and obj.candidate == request.user
        )


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# IsEmployer allows only authenticated users whose role is EMPLOYER.
#
# IsCandidate allows only authenticated users whose role is CANDIDATE.
#
# IsJobOwner is an object-level permission. It allows access only when the job
# object's employer is the user making the request.
#
# IsApplicationOwner is an object-level permission. It allows access only when
# the application object's candidate is the user making the request.
#
# Important decisions that were made and why
#
# Each permission checks request.user.is_authenticated before checking roles or
# object ownership so anonymous users cannot pass permission checks.
#
# getattr is used for role checks so the permission returns False instead of
# crashing if a user-like object has no role attribute.
#
# Job and application ownership are object permissions because they depend on
# the specific database row being accessed.
#
# What you should read and understand before you review the code
#
# Read Django REST Framework custom permissions.
#
# Read the difference between has_permission and has_object_permission.
#
# Read how permission_classes are applied to API views.
#
# ============================================================
# END OF REVIEW
# ============================================================
