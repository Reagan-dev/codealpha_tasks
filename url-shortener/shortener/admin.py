from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ShortURL, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
        "groups",
    )
    search_fields = (
        "email",
        "first_name",
        "last_name",
    )
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = (
        "short_code",
        "truncated_url",
        "click_count",
        "expires_at",
        "created_by",
        "created_at",
    )
    list_filter = (
        "created_at",
        "expires_at",
    )
    search_fields = (
        "short_code",
        "original_url",
        "custom_alias",
    )
    readonly_fields = (
        "click_count",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

    @admin.display(description="Original URL")
    def truncated_url(self, obj):
        return obj.original_url[:50]


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# This file controls how the shortener app models appear in the Django
# admin panel.
#
# CustomUserAdmin registers the custom User model with Django's UserAdmin.
# UserAdmin is used because it already knows how to manage passwords,
# permissions, groups, staff status, and superuser status safely.
#
# CustomUserAdmin.model tells Django admin which model this admin class
# belongs to.
#
# CustomUserAdmin.list_display controls the columns shown on the user list
# page. Email is shown first because this project uses email as the login
# identifier.
#
# CustomUserAdmin.list_filter adds sidebar filters for common user status
# fields. This makes it easier to find staff users, active users, and
# superusers.
#
# CustomUserAdmin.search_fields lets the admin search users by email, first
# name, or last name.
#
# CustomUserAdmin.ordering sorts users by email so the user list is stable
# and easy to scan.
#
# CustomUserAdmin.fieldsets controls the sections shown when editing an
# existing user. It removes username because this custom user model does
# not use username.
#
# CustomUserAdmin.add_fieldsets controls the form shown when creating a new
# user in the admin. It uses email, password1, and password2 because email
# is the identifier for this project.
#
# ShortURLAdmin registers the ShortURL model with a custom admin layout.
# This gives the admin panel a clean table for reviewing shortened links.
#
# ShortURLAdmin.list_display controls the columns shown on the short URL
# list page. It includes the short code, a shortened version of the
# original URL, click count, expiration time, creator, and creation time.
#
# ShortURLAdmin.list_filter adds filters for created_at and expires_at.
# These are useful when checking recent links or expired links.
#
# ShortURLAdmin.search_fields lets the admin search by short code, original
# URL, or custom alias. These are the most likely values someone will know
# when looking for a link.
#
# ShortURLAdmin.readonly_fields prevents click_count, created_at, and
# updated_at from being edited manually. These values should be controlled
# by the application and Django timestamps.
#
# ShortURLAdmin.ordering shows the newest links first. This matches the
# model ordering and is useful for admin review.
#
# truncated_url is a custom method used as a list_display column. It returns
# only the first 50 characters of original_url so very long URLs do not make
# the admin table hard to read.
#
# Important decisions made:
# - UserAdmin was reused instead of writing a user admin from scratch
#   because Django already provides secure user management behavior.
# - The username field was removed from the admin forms because the custom
#   user model uses email as the identifier.
# - Long URLs are truncated only in the admin list display. The database
#   still stores the full original URL.
# - click_count and timestamp fields are read-only because they should be
#   changed by app logic, not typed manually in the admin.
#
# Before reviewing this code, read and understand:
# - How Django admin registration works.
# - How ModelAdmin changes list pages, filters, search, and forms.
# - How UserAdmin handles passwords and permissions.
# - Why custom user models that use email should not show username fields.
# - Why some fields should be read-only in the admin.
#
# ============================================================
# END OF REVIEW
# ============================================================
