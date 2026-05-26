from django.db import models

from menu.models import MenuItem


class InventoryItem(models.Model):
    """Ingredient or stock item used by the restaurant."""

    name = models.CharField(
        max_length=150,
        unique=True,
        help_text="Unique ingredient or stock item name.",
    )
    unit = models.CharField(
        max_length=50,
        help_text="Stock unit, for example kg, litres, or pieces.",
    )
    quantity_in_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Current quantity available in stock.",
    )
    reorder_level = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Minimum quantity allowed before restocking is needed.",
    )
    cost_per_unit = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Purchase cost for one stock unit.",
    )
    last_restocked = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time this item was last restocked.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time this inventory item was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time this inventory item was last updated.",
    )

    class Meta:
        verbose_name = "inventory item"
        verbose_name_plural = "inventory items"
        ordering = ["name"]

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level

    def __str__(self):
        return self.name


class MenuItemIngredient(models.Model):
    """Amount of an inventory item needed to prepare a menu item."""

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="ingredients",
        help_text="Menu item that uses this ingredient.",
    )
    ingredient = models.ForeignKey(
        InventoryItem,
        on_delete=models.PROTECT,
        related_name="menu_item_links",
        help_text="Inventory item required by the menu item.",
    )
    quantity_required = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        help_text="Quantity of this ingredient needed for one menu item.",
    )

    class Meta:
        verbose_name = "menu item ingredient"
        verbose_name_plural = "menu item ingredients"
        ordering = ["menu_item__name", "ingredient__name"]
        unique_together = ["menu_item", "ingredient"]

    def __str__(self):
        return f"{self.menu_item} - {self.ingredient}"


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# InventoryItem stores stock records such as rice, oil, soda, or packaging.
# name is unique so staff do not create duplicate stock items.
#
# unit is a text field because restaurants may measure stock in different
# ways, such as kg, litres, bottles, cartons, or pieces.
#
# quantity_in_stock, reorder_level, and cost_per_unit use DecimalField because
# stock quantities and costs need exact decimal values.
#
# last_restocked is optional because a newly created stock item may not have a
# restock event yet.
#
# is_low_stock is a property that returns True when current stock is less than
# or equal to the reorder level. It is written as a property because it is
# calculated from existing fields and should not be stored separately.
#
# MenuItemIngredient connects menu items to the inventory items needed to make
# them. quantity_required says how much ingredient is needed for one serving.
#
# __str__ methods return simple names or relationships so admin pages and shell
# output are easy to read.
#
# Important decisions that were made and why
#
# MenuItemIngredient uses unique_together so the same ingredient cannot be
# added twice to the same menu item. Staff should update quantity_required
# instead of creating a duplicate row.
#
# Deleting a MenuItem cascades to its ingredient requirements because those
# requirements are only useful for that menu item.
#
# Deleting an InventoryItem is protected while recipes still use it. This
# prevents a recipe from pointing to missing stock data.
#
# What you should read and understand before you review the code
#
# Read Django relationships, especially ForeignKey related_name, CASCADE,
# PROTECT, and unique_together.
#
# Read Python @property so you understand why is_low_stock is called like a
# field but calculated like a method.
#
# ============================================================
# END OF REVIEW
# ============================================================
