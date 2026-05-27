from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CandidateProfile, EmployerProfile, User


class EmployerProfileInline(admin.StackedInline):
    """Show employer profile fields on the user admin page."""

    model = EmployerProfile
    can_delete = False
    extra = 0


class CandidateProfileInline(admin.StackedInline):
    """Show candidate profile fields on the user admin page."""

    model = CandidateProfile
    can_delete = False
    extra = 0


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for the custom user model."""

    inlines = (EmployerProfileInline, CandidateProfileInline)
    list_display = (
        "email",
        "username",
        "role",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
    )
    ordering = ("email",)
    fieldsets = UserAdmin.fieldsets + (
        (
            "Job Board Profile",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "bio",
                    "profile_picture",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Job Board Profile",
            {
                "fields": (
                    "email",
                    "role",
                    "phone_number",
                )
            },
        ),
    )


