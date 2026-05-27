from django.conf import settings
from django.db import models
from django.db.models import Sum

from menu.models import MenuItem
from reservations.models import RestaurantTable


class Order(models.Model):
    """Customer order for dine-in or takeaway service."""

    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "Received"
        PREPARING = "PREPARING", "Preparing"
        READY = "READY", "Ready"
        SERVED = "SERVED", "Served"
        CANCELLED = "CANCELLED", "Cancelled"

    class OrderType(models.TextChoices):
        DINE_IN = "DINE_IN", "Dine in"
        TAKEAWAY = "TAKEAWAY", "Takeaway"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        help_text="Customer who placed this order.",
    )
    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        help_text="Optional table for dine-in orders.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
        help_text="Current preparation and service status of the order.",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total amount calculated from all order items.",
    )
    order_type = models.CharField(
        max_length=20,
        choices=OrderType.choices,
        default=OrderType.DINE_IN,
        help_text="Whether the order is dine-in or takeaway.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time this order was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time this order was last updated.",
    )

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        total_amount = self.items.aggregate(
            total=Sum("subtotal"),
        )["total"] or 0

        if self.total_amount != total_amount:
            self.total_amount = total_amount
            Order.objects.filter(pk=self.pk).update(total_amount=total_amount)

    def __str__(self):
        return f"Order #{self.pk} - {self.customer}"


class OrderItem(models.Model):
    """Single menu item line inside an order."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Order that this line item belongs to.",
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name="order_items",
        help_text="Menu item ordered by the customer.",
    )
    quantity = models.PositiveIntegerField(
        help_text="Number of this menu item ordered.",
    )
    unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Menu item price at the time of ordering.",
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Line total calculated from quantity and unit price.",
    )

    class Meta:
        verbose_name = "order item"
        verbose_name_plural = "order items"
        ordering = ["order", "id"]

    @property
    def calculated_subtotal(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        self.subtotal = self.calculated_subtotal
        super().save(*args, **kwargs)
        self.order.save()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item}"


