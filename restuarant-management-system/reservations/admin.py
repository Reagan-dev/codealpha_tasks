from django.contrib import admin

from .models import Reservation, RestaurantTable


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    """Admin settings for restaurant tables."""

    list_display = ("table_number", "capacity", "location", "is_active")
    list_filter = ("location", "is_active")
    search_fields = ("table_number",)
    ordering = ("table_number",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Admin settings for reservations."""

    list_display = (
        "table",
        "customer",
        "reservation_datetime",
        "party_size",
        "status",
    )
    list_filter = ("status", "reservation_datetime")
    search_fields = ("customer__email", "table__table_number")
    autocomplete_fields = ("table", "customer")
    ordering = ("-reservation_datetime",)


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# RestaurantTableAdmin registers RestaurantTable in the admin so staff can
# manage table numbers, capacity, location, and whether a table is active.
#
# list_display shows the fields staff need when assigning or reviewing tables.
#
# ReservationAdmin registers Reservation in the admin so staff can view and
# manage table bookings.
#
# ReservationAdmin list_display shows the requested fields: table, customer,
# reservation_datetime, party_size, and status.
#
# list_filter helps staff find reservations by status or date.
#
# search_fields lets staff search reservations by customer email or table
# number.
#
# autocomplete_fields makes selecting customers and tables easier as the system
# grows.
#
# Important decisions that were made and why
#
# Reservations are ordered newest first by reservation_datetime because recent
# and upcoming bookings are usually the most important to staff.
#
# Customer search uses customer__email because email is the login field for the
# custom User model.
#
# What you should read and understand before you review the code
#
# Read Django admin search_fields syntax for related models, such as
# customer__email.
#
# Read autocomplete_fields and how it depends on search_fields in the related
# model admin.
#
# ============================================================
# END OF REVIEW
# ============================================================
