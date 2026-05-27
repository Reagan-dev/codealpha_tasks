from rest_framework import serializers

from inventory.models import MenuItemIngredient

from .models import Category, MenuItem


class CategorySerializer(serializers.ModelSerializer):
    """Serialize menu categories."""

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "description",
            "display_order",
            "is_active",
        )


class MenuItemIngredientSerializer(serializers.ModelSerializer):
    """Serialize ingredient details used by a menu item."""

    ingredient_name = serializers.CharField(
        source="ingredient.name",
        read_only=True,
    )
    unit = serializers.CharField(source="ingredient.unit", read_only=True)

    class Meta:
        model = MenuItemIngredient
        fields = ("ingredient_name", "quantity_required", "unit")


class MenuItemListSerializer(serializers.ModelSerializer):
    """Serialize menu item summary data for list endpoints."""

    category_name = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = (
            "id",
            "name",
            "category_name",
            "price",
            "is_available",
            "preparation_time",
            "image",
        )

    def get_category_name(self, obj):
        return obj.category.name


class MenuItemDetailSerializer(MenuItemListSerializer):
    """Serialize full menu item details, including recipe ingredients."""

    ingredients = MenuItemIngredientSerializer(many=True, read_only=True)

    class Meta(MenuItemListSerializer.Meta):
        fields = MenuItemListSerializer.Meta.fields + (
            "description",
            "ingredients",
        )


