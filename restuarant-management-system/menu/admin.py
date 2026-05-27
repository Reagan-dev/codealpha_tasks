from django.contrib import admin

from inventory.models import MenuItemIngredient

from .models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin settings for menu categories."""

    list_display = ("name", "display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("display_order", "name")


class MenuItemIngredientInline(admin.TabularInline):
    """Inline ingredient requirements for a menu item."""

    model = MenuItemIngredient
    extra = 1
    fields = ("ingredient", "quantity_required")
    autocomplete_fields = ("ingredient",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """Admin settings for menu items."""

    list_display = (
        "name",
        "category",
        "price",
        "is_available",
        "preparation_time",
    )
    list_filter = ("category", "is_available")
    search_fields = ("name", "description")
    ordering = ("category__display_order", "name")
    autocomplete_fields = ("category",)
    inlines = (MenuItemIngredientInline,)


