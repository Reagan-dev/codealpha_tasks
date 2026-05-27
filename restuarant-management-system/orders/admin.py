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


