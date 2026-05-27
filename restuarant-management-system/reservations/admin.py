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


