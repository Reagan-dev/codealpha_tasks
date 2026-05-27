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


