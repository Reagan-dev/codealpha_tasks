from rest_framework.permissions import BasePermission


class IsStaff(BasePermission):
    """Allow access only to staff and manager users."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) in ("STAFF", "MANAGER")
        )


class IsManager(BasePermission):
    """Allow access only to manager users."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "MANAGER"
        )


class IsCustomer(BasePermission):
    """Allow access only to customer users."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "CUSTOMER"
        )


class IsOrderOwner(BasePermission):
    """Allow object access only to the customer who owns the order."""

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and obj.customer == request.user
        )


class IsReservationOwner(BasePermission):
    """Allow object access only to the customer who owns the reservation."""

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and obj.customer == request.user
        )


