from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "role",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "role",
        "is_active",
        "date_joined",
    )
    search_fields = (
        "email",
        "username",
    )
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Profile",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "bio",
                ),
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Profile",
            {
                "fields": (
                    "email",
                    "role",
                    "phone_number",
                    "bio",
                ),
            },
        ),
    )


