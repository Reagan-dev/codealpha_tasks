from django.conf import settings
from django.db import models


class RestaurantTable(models.Model):
    """Physical table that can be assigned to reservations and orders."""

    class Location(models.TextChoices):
        INDOOR = "INDOOR", "Indoor"
        OUTDOOR = "OUTDOOR", "Outdoor"
        PRIVATE = "PRIVATE", "Private"

    table_number = models.PositiveIntegerField(
        unique=True,
        help_text="Unique table number used by staff.",
    )
    capacity = models.PositiveIntegerField(
        help_text="Maximum number of guests this table can seat.",
    )
    location = models.CharField(
        max_length=20,
        choices=Location.choices,
        help_text="Restaurant area where this table is located.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Controls whether this table can be used for bookings.",
    )

    class Meta:
        verbose_name = "restaurant table"
        verbose_name_plural = "restaurant tables"
        ordering = ["table_number"]

    def __str__(self):
        return f"Table {self.table_number}"


class Reservation(models.Model):
    """Customer booking for a restaurant table at a specific time."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.PROTECT,
        related_name="reservations",
        help_text="Table assigned to this reservation.",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
        help_text="Customer who made this reservation.",
    )
    reservation_datetime = models.DateTimeField(
        help_text="Date and time the reservation begins.",
    )
    duration_minutes = models.PositiveIntegerField(
        default=90,
        help_text="Expected reservation duration in minutes.",
    )
    party_size = models.PositiveIntegerField(
        help_text="Number of guests included in the reservation.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current reservation status.",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Optional notes or special requests for the reservation.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time this reservation was created.",
    )

    class Meta:
        verbose_name = "reservation"
        verbose_name_plural = "reservations"
        ordering = ["-reservation_datetime"]

    def __str__(self):
        return f"{self.customer} - {self.table} at {self.reservation_datetime}"


