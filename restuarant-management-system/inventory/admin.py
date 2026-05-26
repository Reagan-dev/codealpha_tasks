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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# InventoryItemAdmin registers InventoryItem in the Django admin so staff can
# manage stock levels, reorder levels, unit costs, and restock dates.
#
# list_display includes low_stock_status so staff can quickly see whether an
# item needs restocking.
#
# low_stock_status reads the model's is_low_stock property. It returns a red
# "Low" label when stock is at or below the reorder level and a green "OK"
# label when stock is healthy.
#
# format_html is used because Django admin escapes normal strings. format_html
# safely returns small HTML snippets for colored display.
#
# MenuItemIngredientAdmin registers the recipe link model separately. This
# gives staff a direct place to review and edit all menu-item-to-ingredient
# relationships.
#
# Important decisions that were made and why
#
# The colored low-stock value is calculated in admin instead of being stored in
# the database because the model already knows how to calculate is_low_stock.
#
# MenuItemIngredient is registered separately even though it is also used as an
# inline in MenuItemAdmin. The inline is convenient for editing one menu item,
# while the separate admin page is useful for reviewing all ingredient links.
#
# What you should read and understand before you review the code
#
# Read Django's @admin.display decorator.
#
# Read Django's format_html helper and why it is safer than building raw HTML
# strings manually.
#
# Read how list_display can include model fields and ModelAdmin methods.
#
# ============================================================
# END OF REVIEW
# ============================================================
