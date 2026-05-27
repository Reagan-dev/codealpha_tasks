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


