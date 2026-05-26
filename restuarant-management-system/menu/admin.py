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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# CategoryAdmin registers Category in the admin so staff can manage menu
# sections such as starters, mains, desserts, or drinks.
#
# list_display shows the category name, display order, and active status so
# staff can quickly see how the menu is organized.
#
# MenuItemIngredientInline lets staff add recipe ingredients while editing a
# menu item. This is useful because ingredient requirements belong naturally
# with the menu item being prepared.
#
# MenuItemAdmin registers MenuItem in the admin. Its list_display shows the
# requested fields: name, category, price, is_available, and preparation_time.
#
# list_filter helps staff narrow menu items by category or availability.
#
# search_fields helps staff find a menu item by name or description.
#
# autocomplete_fields makes category and ingredient selection easier when the
# database grows.
#
# Important decisions that were made and why
#
# The ingredient inline lives under MenuItem because recipe setup is easiest
# while viewing the menu item itself.
#
# MenuItemIngredient is imported from inventory.models because inventory owns
# the model that connects menu items to stock items.
#
# What you should read and understand before you review the code
#
# Read Django admin inlines, especially TabularInline.
#
# Read list_display, list_filter, search_fields, ordering, and
# autocomplete_fields in Django's ModelAdmin documentation.
#
# ============================================================
# END OF REVIEW
# ============================================================
