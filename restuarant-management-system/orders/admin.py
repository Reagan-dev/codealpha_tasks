from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline order items for an order."""

    model = OrderItem
    extra = 1
    fields = ("menu_item", "quantity", "unit_price", "subtotal")
    readonly_fields = ("subtotal",)
    autocomplete_fields = ("menu_item",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin settings for customer orders."""

    list_display = (
        "id",
        "customer",
        "table",
        "status",
        "order_type",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "order_type", "created_at")
    search_fields = ("customer__email", "table__table_number")
    autocomplete_fields = ("customer", "table")
    readonly_fields = ("total_amount",)
    ordering = ("-created_at",)
    inlines = (OrderItemInline,)


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# OrderItemInline lets staff add or edit order items directly on the order
# page. This is useful because order items belong to one order.
#
# The inline shows menu_item, quantity, unit_price, and subtotal as requested.
#
# subtotal is readonly because the OrderItem model calculates it from quantity
# and unit_price. Staff should change quantity or unit_price, not type subtotal
# by hand.
#
# OrderAdmin registers Order in the admin. Its list_display shows the requested
# fields: id, customer, table, status, order_type, total_amount, and created_at.
#
# list_filter helps staff find orders by status, order type, or creation date.
#
# search_fields lets staff search by customer email or table number.
#
# total_amount is readonly because the Order model recalculates it from all
# related order items.
#
# Important decisions that were made and why
#
# OrderItem is managed as an inline instead of a separate registered admin page
# because line items are usually edited in the context of their parent order.
#
# autocomplete_fields is used for customer, table, and menu_item so the admin
# remains usable when there are many users, tables, and menu items.
#
# What you should read and understand before you review the code
#
# Read Django admin TabularInline and readonly_fields.
#
# Read how parent objects and inline child objects are saved in the Django
# admin.
#
# Read why calculated money fields should usually be readonly in admin.
#
# ============================================================
# END OF REVIEW
# ============================================================
