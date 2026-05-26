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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# InventoryItemSerializer converts InventoryItem model objects to and from API
# data. It includes all inventory fields plus is_low_stock.
#
# is_low_stock is read-only because it is calculated by the model from
# quantity_in_stock and reorder_level. API users should not set it manually.
#
# RestockSerializer is a plain Serializer because restocking is an action, not
# a full InventoryItem create or update request.
#
# quantity_to_add is write-only because it is input for an action. The API does
# not need to return the same value as a stored model field.
#
# validate_quantity_to_add ensures stock cannot be restocked by zero or a
# negative number.
#
# Important decisions that were made and why
#
# RestockSerializer uses DecimalField because inventory quantities can include
# decimal amounts such as kilograms or litres.
#
# The restock action is kept separate from InventoryItemSerializer so normal
# inventory updates and restock operations can have different validation rules.
#
# What you should read and understand before you review the code
#
# Read DRF ModelSerializer and plain Serializer differences.
#
# Read field-level validation methods such as validate_quantity_to_add.
#
# Read why calculated model properties should be exposed as read-only fields.
#
# ============================================================
# END OF REVIEW
# ============================================================
