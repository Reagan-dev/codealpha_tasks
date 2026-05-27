from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin settings for the custom user model."""

    list_display = ("email", "role", "is_active")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Restaurant Profile",
            {
                "fields": ("role", "phone_number"),
            },
        ),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (
            "Restaurant Profile",
            {
                "fields": ("email", "role", "phone_number"),
            },
        ),
    )


