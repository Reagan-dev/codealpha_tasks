from django.contrib import admin
from django.utils.html import format_html

from .models import InventoryItem, MenuItemIngredient


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    """Admin settings for inventory items."""

    list_display = (
        "name",
        "unit",
        "quantity_in_stock",
        "reorder_level",
        "cost_per_unit",
        "low_stock_status",
        "last_restocked",
    )
    list_filter = ("unit",)
    search_fields = ("name",)
    ordering = ("name",)

    @admin.display(description="Low stock")
    def low_stock_status(self, obj):
        """Return a colored stock status label for the admin list page."""
        if obj.is_low_stock:
            return format_html(
                '<span style="color: #b91c1c; font-weight: 600;">Low</span>'
            )

        return format_html(
            '<span style="color: #15803d; font-weight: 600;">OK</span>'
        )


@admin.register(MenuItemIngredient)
class MenuItemIngredientAdmin(admin.ModelAdmin):
    """Admin settings for menu item ingredient requirements."""

    list_display = ("menu_item", "ingredient", "quantity_required")
    list_filter = ("ingredient",)
    search_fields = ("menu_item__name", "ingredient__name")
    autocomplete_fields = ("menu_item", "ingredient")
    ordering = ("menu_item__name", "ingredient__name")


