from rest_framework import serializers

from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    """Serialize inventory item data."""

    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = (
            "id",
            "name",
            "unit",
            "quantity_in_stock",
            "reorder_level",
            "cost_per_unit",
            "last_restocked",
            "created_at",
            "updated_at",
            "is_low_stock",
        )
        read_only_fields = ("created_at", "updated_at", "is_low_stock")


class RestockSerializer(serializers.Serializer):
    """Validate a positive quantity before restocking inventory."""

    quantity_to_add = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        write_only=True,
    )

    def validate_quantity_to_add(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity to add must be greater than zero."
            )

        return value


