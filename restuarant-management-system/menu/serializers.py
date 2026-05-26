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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# CategorySerializer converts Category model objects to and from API data.
# It includes the fields needed to show and manage menu sections.
#
# MenuItemIngredientSerializer shows the ingredient name, quantity required,
# and unit for a menu item. ingredient_name and unit come from the related
# InventoryItem so API users do not need to make another request to understand
# the ingredient.
#
# MenuItemListSerializer shows the short version of a menu item for list
# pages. category_name is a method field so the API returns readable category
# text instead of only a database ID.
#
# get_category_name returns the name of the related category.
#
# MenuItemDetailSerializer extends MenuItemListSerializer and adds description
# plus nested ingredients. This avoids duplicating the shared menu item fields.
#
# Important decisions that were made and why
#
# List and detail serializers are separate because list endpoints should stay
# smaller, while detail endpoints can include fuller data.
#
# Ingredients are read-only in the menu detail serializer because ingredient
# editing belongs to inventory or admin workflows.
#
# What you should read and understand before you review the code
#
# Read DRF ModelSerializer basics.
#
# Read SerializerMethodField and source for related-object fields.
#
# Read nested serializers with many=True and read_only=True.
#
# ============================================================
# END OF REVIEW
# ============================================================
