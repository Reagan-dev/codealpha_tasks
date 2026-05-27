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


