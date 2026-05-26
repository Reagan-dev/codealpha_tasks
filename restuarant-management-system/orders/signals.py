import logging

from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from inventory.models import InventoryItem, MenuItemIngredient

from .models import Order, OrderItem


logger = logging.getLogger(__name__)


def _deduct_inventory_item(ingredient_link, order_item):
    """Deduct one ingredient from stock for a newly created order item."""
    ingredient = ingredient_link.ingredient
    quantity_to_deduct = (
        ingredient_link.quantity_required * order_item.quantity
    )

    InventoryItem.objects.filter(pk=ingredient.pk).update(
        quantity_in_stock=F("quantity_in_stock") - quantity_to_deduct
    )
    ingredient.refresh_from_db(fields=("quantity_in_stock", "reorder_level"))

    if ingredient.quantity_in_stock < 0:
        logger.warning(
            "Inventory item '%s' is below zero after order item %s. "
            "Current stock: %s %s.",
            ingredient.name,
            order_item.pk,
            ingredient.quantity_in_stock,
            ingredient.unit,
        )

    if ingredient.is_low_stock:
        logger.warning(
            "Inventory item '%s' is low. Current stock: %s %s. "
            "Reorder level: %s %s.",
            ingredient.name,
            ingredient.quantity_in_stock,
            ingredient.unit,
            ingredient.reorder_level,
            ingredient.unit,
        )


def _restore_inventory_item(ingredient_link, order_item):
    """Add one ingredient quantity back to stock for a cancelled order."""
    quantity_to_restore = (
        ingredient_link.quantity_required * order_item.quantity
    )

    InventoryItem.objects.filter(pk=ingredient_link.ingredient_id).update(
        quantity_in_stock=F("quantity_in_stock") + quantity_to_restore
    )


@receiver(post_save, sender=OrderItem)
def deduct_inventory_on_order_item_created(sender, instance, created, **kwargs):
    """
    Deduct inventory when a new order item is created.

    The handler only runs for new OrderItem rows and skips cancelled orders.
    For each ingredient linked to the ordered menu item, it deducts
    quantity_required multiplied by the ordered quantity. The update uses an
    F() expression so the database performs the arithmetic atomically and two
    orders cannot overwrite each other's stock changes.
    """
    if not created or instance.order.status == Order.Status.CANCELLED:
        return

    ingredient_links = MenuItemIngredient.objects.select_related(
        "ingredient"
    ).filter(menu_item=instance.menu_item)

    for ingredient_link in ingredient_links:
        _deduct_inventory_item(ingredient_link, instance)


@receiver(pre_save, sender=Order)
def store_previous_order_status(sender, instance, **kwargs):
    """
    Store the order's previous status before saving.

    Django's post_save signal receives the saved object but does not include
    the old database value. This helper saves the previous status on the
    instance so the cancellation handler can tell whether the status actually
    changed to CANCELLED.
    """
    if not instance.pk:
        instance._previous_status = None
        return

    instance._previous_status = (
        Order.objects.filter(pk=instance.pk)
        .values_list("status", flat=True)
        .first()
    )


@receiver(post_save, sender=Order)
def restore_inventory_on_order_cancelled(sender, instance, created, **kwargs):
    """
    Restore inventory when an existing order changes to CANCELLED.

    The handler only runs when an order was previously not cancelled and is now
    cancelled. It loops through every OrderItem in the order and adds each
    ingredient quantity back to stock with an F() expression, keeping the
    database update atomic and safe under concurrent requests.
    """
    previous_status = getattr(instance, "_previous_status", None)

    if (
        created
        or previous_status == Order.Status.CANCELLED
        or instance.status != Order.Status.CANCELLED
    ):
        return

    order_items = instance.items.select_related("menu_item")

    for order_item in order_items:
        ingredient_links = MenuItemIngredient.objects.filter(
            menu_item=order_item.menu_item
        )

        for ingredient_link in ingredient_links:
            _restore_inventory_item(ingredient_link, order_item)


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# logger creates a logger for this file. It is used to warn staff or
# developers when stock becomes negative or low.
#
# _deduct_inventory_item handles the stock deduction for one ingredient. It is
# a helper so the signal handler stays easy to read.
#
# _restore_inventory_item handles adding stock back for one ingredient when an
# order is cancelled.
#
# deduct_inventory_on_order_item_created is a post_save signal for OrderItem.
# It runs only when a new order item is created. It skips cancelled orders
# because cancelled orders should not reduce stock.
#
# For every ingredient linked to the ordered menu item, the signal deducts
# quantity_required multiplied by the order item quantity.
#
# The deduction uses F() so the database updates the stock number atomically.
# This avoids race conditions when two orders are created at the same time.
#
# If stock becomes negative, the code logs a warning but does not raise an
# error. The order can continue, and staff can fix the stock problem later.
#
# If stock is at or below the reorder level after deduction, the code logs a
# low-stock warning.
#
# store_previous_order_status is a pre_save signal for Order. It stores the old
# status on the instance because post_save does not provide the previous value.
#
# restore_inventory_on_order_cancelled is a post_save signal for Order. It runs
# only when an existing order changes from a non-cancelled status to CANCELLED.
# It adds the deducted ingredient quantities back to stock.
#
# Important decisions that were made and why
#
# A small pre_save helper is used because detecting "status changed to
# CANCELLED" is not possible from post_save alone.
#
# Stock is allowed to become negative because the request said to log a warning
# if stock would go below zero and not crash.
#
# F() expressions are used for both deduction and restoration so stock updates
# are handled safely by the database.
#
# What you should read and understand before you review the code
#
# Read Django signals, especially pre_save and post_save.
#
# Read F() expressions and why they prevent lost updates during concurrent
# database writes.
#
# Read Python logging so you understand where warning messages go.
#
# ============================================================
# END OF REVIEW
# ============================================================
