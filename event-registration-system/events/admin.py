from django.contrib import admin

from .models import Category, Event, Registration


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
    )
    search_fields = ("name",)
    readonly_fields = ("created_at",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "organizer",
        "category",
        "start_datetime",
        "capacity",
        "current_registrations",
        "status",
    )
    list_filter = (
        "status",
        "category",
        "start_datetime",
    )
    search_fields = (
        "title",
        "organizer__email",
        "location",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "current_registrations",
        "spots_left",
    )

    @admin.display(description="Current registrations")
    def current_registrations(self, obj):
        return obj.current_registrations

    @admin.display(description="Spots left")
    def spots_left(self, obj):
        return obj.spots_left


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_number",
        "user",
        "event",
        "status",
        "registered_at",
    )
    list_filter = (
        "status",
        "event",
        "registered_at",
    )
    search_fields = (
        "ticket_number",
        "user__email",
        "event__title",
    )
    readonly_fields = (
        "ticket_number",
        "registered_at",
    )


