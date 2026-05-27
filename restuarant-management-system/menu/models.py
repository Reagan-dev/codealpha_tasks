from django.db import models


class Category(models.Model):
    """Group menu items into sections such as starters or drinks."""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique category name shown on the menu.",
    )
    description = models.TextField(
        help_text="Short description of the category.",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear earlier in the menu.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Controls whether this category is visible to customers.",
    )

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Food or drink item that can be ordered by a customer."""

    name = models.CharField(
        max_length=150,
        help_text="Name of the menu item shown to customers.",
    )
    description = models.TextField(
        help_text="Customer-facing description of the menu item.",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="menu_items",
        help_text="Category where this menu item appears.",
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Selling price of the menu item.",
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Controls whether customers can currently order this item.",
    )
    image = models.ImageField(
        upload_to="menu_items/",
        null=True,
        blank=True,
        help_text="Optional photo of the menu item.",
    )
    preparation_time = models.PositiveIntegerField(
        help_text="Estimated preparation time in minutes.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time this menu item was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time this menu item was last updated.",
    )

    class Meta:
        verbose_name = "menu item"
        verbose_name_plural = "menu items"
        ordering = ["category__display_order", "name"]

    def __str__(self):
        return self.name


