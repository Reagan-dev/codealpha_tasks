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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# UserAdmin registers the custom User model in the Django admin.
#
# It extends DjangoUserAdmin instead of plain ModelAdmin because User inherits
# from AbstractUser. DjangoUserAdmin already knows how to handle passwords,
# permissions, staff status, groups, and superuser settings.
#
# list_display shows email, role, and is_active because those are the most
# important fields for quickly reviewing user accounts.
#
# list_filter lets an admin filter users by role and account status.
#
# search_fields lets an admin find users by email, username, or name.
#
# fieldsets adds role and phone_number to the existing user edit page.
#
# add_fieldsets adds email, role, and phone_number to the create-user page.
#
# Important decisions that were made and why
#
# The admin keeps Django's default user admin behavior so password and
# permission management continue to work correctly.
#
# The list display is intentionally short because the request only asked for
# email, role, and is_active.
#
# What you should read and understand before you review the code
#
# Read Django's ModelAdmin and UserAdmin documentation.
#
# Read how fieldsets and add_fieldsets control the admin edit and create pages.
#
# ============================================================
# END OF REVIEW
# ============================================================
