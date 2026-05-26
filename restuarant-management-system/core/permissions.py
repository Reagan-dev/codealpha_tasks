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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# IsStaff is a DRF permission class. It allows authenticated users whose role
# is STAFF or MANAGER.
#
# IsManager is a DRF permission class. It allows authenticated users whose role
# is MANAGER.
#
# IsCustomer is a DRF permission class. It allows authenticated users whose
# role is CUSTOMER.
#
# IsOrderOwner is an object-level permission. It allows access only when the
# order's customer is the same user making the request.
#
# IsReservationOwner is an object-level permission. It allows access only when
# the reservation's customer is the same user making the request.
#
# Important decisions that were made and why
#
# Each permission checks request.user.is_authenticated first so anonymous users
# cannot pass because they happen to have a missing or unexpected role value.
#
# getattr is used for role checks so the permission returns False instead of
# crashing if a request user does not have a role attribute.
#
# The role values are compared as strings because the User model stores those
# exact values in the database.
#
# What you should read and understand before you review the code
#
# Read Django REST Framework custom permissions.
#
# Read the difference between has_permission and has_object_permission.
#
# Read how permission classes are applied to API views and viewsets.
#
# ============================================================
# END OF REVIEW
# ============================================================
