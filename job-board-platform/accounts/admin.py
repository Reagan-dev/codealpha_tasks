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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# EmployerProfileInline lets admins edit an employer's company profile from
# the same page as the related user.
#
# CandidateProfileInline lets admins edit a candidate's professional profile
# from the same page as the related user.
#
# CustomUserAdmin extends Django's UserAdmin so the custom User model keeps
# Django's normal user management features.
#
# list_display shows email, username, role, active status, and staff status so
# admins can scan users quickly.
#
# list_filter lets admins filter users by role and account flags.
#
# search_fields lets admins find users by email, username, or name.
#
# fieldsets adds job-board fields to the normal user edit form.
#
# add_fieldsets adds email, role, and phone number to the user creation form.
#
# Important decisions that were made and why
#
# StackedInline is used because employer and candidate profiles have multiple
# fields and are easier to read vertically.
#
# The profile inlines use can_delete=False so profile rows are not removed by
# accident while editing a user.
#
# UserAdmin is reused instead of writing admin behavior from scratch.
#
# What you should read and understand before you review the code
#
# Read Django ModelAdmin basics.
#
# Read Django UserAdmin customization.
#
# Read StackedInline and how OneToOne profile models appear in admin.
#
# ============================================================
# END OF REVIEW
# ============================================================
