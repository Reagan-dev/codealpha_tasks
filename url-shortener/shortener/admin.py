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


