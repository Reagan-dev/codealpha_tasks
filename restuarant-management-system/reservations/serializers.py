from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Reservation, RestaurantTable


class RestaurantTableSerializer(serializers.ModelSerializer):
    """Serialize restaurant table data."""

    class Meta:
        model = RestaurantTable
        fields = ("id", "table_number", "capacity", "location", "is_active")


class ReservationCreateSerializer(serializers.ModelSerializer):
    """Validate and serialize reservation creation requests."""

    class Meta:
        model = Reservation
        fields = (
            "table",
            "reservation_datetime",
            "party_size",
            "duration_minutes",
            "notes",
        )

    def validate_reservation_datetime(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Reservation date and time must be in the future."
            )

        return value

    def validate(self, attrs):
        table = attrs["table"]
        party_size = attrs["party_size"]
        starts_at = attrs["reservation_datetime"]
        duration_minutes = attrs.get("duration_minutes", 90)
        ends_at = starts_at + timedelta(minutes=duration_minutes)

        if party_size > table.capacity:
            raise serializers.ValidationError(
                {
                    "party_size": (
                        "Party size cannot be greater than table capacity."
                    )
                }
            )

        if self._has_conflicting_reservation(table, starts_at, ends_at):
            raise serializers.ValidationError(
                {
                    "reservation_datetime": (
                        "This table already has a conflicting reservation."
                    )
                }
            )

        return attrs

    def _has_conflicting_reservation(self, table, starts_at, ends_at):
        reservations = Reservation.objects.filter(table=table).exclude(
            status__in=(
                Reservation.Status.CANCELLED,
                Reservation.Status.COMPLETED,
            )
        )

        for reservation in reservations:
            existing_starts_at = reservation.reservation_datetime
            existing_ends_at = existing_starts_at + timedelta(
                minutes=reservation.duration_minutes
            )

            if existing_starts_at < ends_at and existing_ends_at > starts_at:
                return True

        return False


class ReservationDetailSerializer(serializers.ModelSerializer):
    """Serialize reservation details for read endpoints."""

    table_number = serializers.IntegerField(
        source="table.table_number",
        read_only=True,
    )
    customer_email = serializers.EmailField(
        source="customer.email",
        read_only=True,
    )

    class Meta:
        model = Reservation
        fields = (
            "id",
            "table",
            "table_number",
            "customer",
            "customer_email",
            "reservation_datetime",
            "duration_minutes",
            "party_size",
            "status",
            "notes",
            "created_at",
        )
        read_only_fields = fields


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# RestaurantTableSerializer converts RestaurantTable objects to and from API
# data. It includes the table number, capacity, location, and active status.
#
# ReservationCreateSerializer handles reservation input. It includes only the
# fields a customer or staff member should send when creating a booking.
#
# validate_reservation_datetime makes sure the booking starts in the future.
#
# validate checks rules that need more than one field. It confirms the party
# size fits the selected table and checks whether the table is already booked
# during the requested time window.
#
# _has_conflicting_reservation compares the requested reservation window with
# existing active reservation windows for the same table.
#
# ReservationDetailSerializer returns the full reservation data plus readable
# table_number and customer_email fields.
#
# Important decisions that were made and why
#
# CANCELLED and COMPLETED reservations are ignored during conflict checks
# because they should not block future bookings.
#
# The overlap check uses the standard rule: an existing booking conflicts when
# it starts before the new booking ends and ends after the new booking starts.
#
# Customer is not included in the create serializer because the view should set
# it from request.user.
#
# What you should read and understand before you review the code
#
# Read DRF object-level validation with validate.
#
# Read timezone-aware datetime handling in Django.
#
# Read how date range overlap checks work.
#
# ============================================================
# END OF REVIEW
# ============================================================
