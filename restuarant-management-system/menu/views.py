from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from core.permissions import IsStaff

from .models import Category, MenuItem
from .serializers import (
    CategorySerializer,
    MenuItemDetailSerializer,
    MenuItemListSerializer,
)


def _get_category_from_request(request, required=False):
    category_id = request.data.get("category")

    if not category_id:
        if required:
            raise ValidationError({"category": "This field is required."})

        return None

    try:
        return Category.objects.get(pk=category_id)
    except (TypeError, ValueError, Category.DoesNotExist) as exc:
        raise ValidationError(
            {"category": "A valid category ID is required."}
        ) from exc


class CategoryListView(generics.ListAPIView):
    """Return menu categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)


class MenuItemListView(generics.ListAPIView):
    """Return menu items, optionally filtered by category or availability."""

    serializer_class = MenuItemListSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = MenuItem.objects.select_related("category").all()
        category = self.request.query_params.get("category")
        available = self.request.query_params.get("available")

        if category:
            if category.isdigit():
                queryset = queryset.filter(category_id=category)
            else:
                queryset = queryset.filter(category__name__iexact=category)

        if available is not None:
            available = available.lower()

            if available == "true":
                queryset = queryset.filter(is_available=True)
            elif available == "false":
                queryset = queryset.filter(is_available=False)
            else:
                raise ValidationError(
                    {"available": "Use true or false."}
                )

        return queryset


class MenuItemDetailView(generics.RetrieveAPIView):
    """Return one menu item."""

    queryset = MenuItem.objects.select_related("category").prefetch_related(
        "ingredients__ingredient"
    )
    serializer_class = MenuItemDetailSerializer
    permission_classes = (AllowAny,)


class MenuItemCreateView(generics.CreateAPIView):
    """Create a menu item."""

    queryset = MenuItem.objects.all()
    serializer_class = MenuItemDetailSerializer
    permission_classes = (IsStaff,)

    def perform_create(self, serializer):
        category = _get_category_from_request(self.request, required=True)
        serializer.save(category=category)


class MenuItemUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a menu item."""

    http_method_names = ("get", "patch", "delete", "head", "options")
    queryset = MenuItem.objects.select_related("category").prefetch_related(
        "ingredients__ingredient"
    )
    serializer_class = MenuItemDetailSerializer
    permission_classes = (IsStaff,)

    def perform_update(self, serializer):
        category = _get_category_from_request(self.request)

        if category is None:
            serializer.save()
            return

        serializer.save(category=category)



