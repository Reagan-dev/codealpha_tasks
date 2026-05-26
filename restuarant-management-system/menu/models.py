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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# Category represents a menu section, for example starters, mains, desserts,
# or drinks. It has a unique name so duplicate sections are not created by
# accident.
#
# display_order lets staff control the order of categories without renaming
# them. is_active lets the restaurant hide a whole category without deleting
# old data.
#
# MenuItem represents one sellable food or drink. It belongs to a Category so
# the menu can be grouped clearly.
#
# category uses PROTECT so a category cannot be deleted while menu items still
# depend on it. This protects order history and menu structure.
#
# price uses DecimalField because money should not be stored with floating
# point numbers.
#
# image is optional because not every menu item needs a photo immediately.
#
# preparation_time stores minutes as a positive integer because preparation
# estimates should be simple whole-minute values.
#
# created_at and updated_at are automatic timestamps for auditing and sorting.
#
# __str__ returns the name because that is the most useful display value in
# admin pages, serializers, and shell output.
#
# Important decisions that were made and why
#
# Category deletion is protected instead of cascading to MenuItem. Deleting a
# category should not silently delete menu items.
#
# The image upload path is "menu_items/" so uploaded menu photos are grouped
# under one media folder.
#
# What you should read and understand before you review the code
#
# Read Django model field basics, especially CharField, TextField,
# BooleanField, DecimalField, ImageField, DateTimeField, and ForeignKey.
#
# Read on_delete behavior, especially PROTECT, so you understand what happens
# when a related object is deleted.
#
# ============================================================
# END OF REVIEW
# ============================================================
