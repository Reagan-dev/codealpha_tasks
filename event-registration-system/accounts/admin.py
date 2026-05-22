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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# UserAdmin customizes how the custom User model appears in the Django admin.
# It extends Django's built-in UserAdmin so password management, permissions,
# groups, and user creation still work the normal Django way.
#
# list_display controls the columns shown on the user list page. Email,
# username, role, active status, and join date are shown because they are the
# most useful fields when reviewing accounts.
#
# list_filter adds sidebar filters for role, active status, and join date so an
# admin can quickly narrow down users.
#
# search_fields allows admins to search users by email or username.
#
# fieldsets adds the custom profile fields to the edit-user page. Without this,
# role, phone_number, and bio would exist in the database but would not be easy
# to edit in the admin.
#
# add_fieldsets adds email and profile fields to the create-user page in the
# admin.
#
# Important decisions that were made and why
#
# BaseUserAdmin was used instead of plain ModelAdmin because User models need
# special admin behavior for passwords and permissions.
#
# The admin registration uses @admin.register(User) because it keeps the model
# and admin class connected clearly in one place.
#
# What you should read and understand before you review the code
#
# Read Django's ModelAdmin options: list_display, list_filter, search_fields,
# fieldsets, and add_fieldsets.
#
# Read Django's custom user admin documentation so you understand why extending
# UserAdmin is safer than building the user admin from scratch.
#
# ============================================================
# END OF REVIEW
# ============================================================
