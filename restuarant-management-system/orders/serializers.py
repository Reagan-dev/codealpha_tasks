from django.db import transaction
from rest_framework import serializers

from reservations.models import RestaurantTable

from .models import Order, OrderItem


class OrderItemCreateSerializer(serializers.ModelSerializer):
    """Validate order item input for order creation."""

    class Meta:
        model = OrderItem
        fields = ("menu_item", "quantity")

    def validate_menu_item(self, value):
        if not value.is_available:
            raise serializers.ValidationError(
                "This menu item is not currently available."
            )

        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )

        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    """Validate and create an order with nested order items."""

    table = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        queryset=RestaurantTable.objects.all(),
        required=False,
    )
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ("table", "order_type", "items")

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one order item is required."
            )

        return value

    def create(self, validated_data):
        request = self.context.get("request")
        items_data = validated_data.pop("items")

        if request is None or request.user.is_anonymous:
            raise serializers.ValidationError(
                "An authenticated customer is required to create an order."
            )

        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user,
                **validated_data,
            )

            for item_data in items_data:
                menu_item = item_data["menu_item"]
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=item_data["quantity"],
                    unit_price=menu_item.price,
                    subtotal=0,
                )

            order.refresh_from_db()

        return order


class OrderItemDetailSerializer(serializers.ModelSerializer):
    """Serialize order item details for read endpoints."""

    menu_item_name = serializers.CharField(
        source="menu_item.name",
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = ("menu_item_name", "quantity", "unit_price", "subtotal")


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serialize full order details with nested order items."""

    customer_email = serializers.EmailField(
        source="customer.email",
        read_only=True,
    )
    table_number = serializers.IntegerField(
        source="table.table_number",
        read_only=True,
    )
    items = OrderItemDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer_email",
            "table_number",
            "status",
            "order_type",
            "total_amount",
            "created_at",
            "items",
        )


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Validate allowed order status transitions."""

    allowed_transitions = {
        Order.Status.RECEIVED: {
            Order.Status.PREPARING,
            Order.Status.CANCELLED,
        },
        Order.Status.PREPARING: {Order.Status.READY, Order.Status.CANCELLED},
        Order.Status.READY: {Order.Status.SERVED, Order.Status.CANCELLED},
        Order.Status.SERVED: {Order.Status.CANCELLED},
        Order.Status.CANCELLED: set(),
    }

    class Meta:
        model = Order
        fields = ("status",)

    def validate_status(self, value):
        order = self.instance

        if order is None:
            return value

        allowed_statuses = self.allowed_transitions.get(order.status, set())

        if value == order.status:
            return value

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Cannot change order status from {order.status} to {value}."
            )

        return value


