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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# _get_category_from_request reads the category ID from request data and
# returns the matching Category. It is used by create and update because the
# existing menu serializers expose category_name for reading, but not category
# as a writable field.
#
# CategoryListView returns all menu categories. It uses ListAPIView because
# this endpoint only needs to list rows and does not need custom response
# code.
#
# MenuItemListView returns menu item summaries. It supports ?category= and
# ?available= filters in get_queryset because filters belong close to the
# database query.
#
# MenuItemDetailView returns one menu item with full detail data. It uses
# RetrieveAPIView because the endpoint only reads a single object.
#
# MenuItemCreateView creates menu items. It uses IsStaff because only staff
# and managers should manage the restaurant menu.
#
# MenuItemUpdateView retrieves, patches, or deletes a menu item through the
# staff management endpoint. It uses RetrieveUpdateDestroyAPIView because that
# generic view already provides those object-level actions.
#
# Important decisions that were made and why
#
# select_related is used for category because every menu item has one category
# and this avoids extra database queries.
#
# prefetch_related is used for ingredients on detail endpoints because
# ingredients are a reverse relationship and need a separate efficient query.
#
# The available filter accepts true and false. Invalid values return a clear
# validation error instead of silently returning confusing results.
#
# What you should read and understand before you review the code
#
# Read DRF generic views, especially ListAPIView, RetrieveAPIView,
# CreateAPIView, and RetrieveUpdateDestroyAPIView.
#
# Read get_queryset and how query parameters are used for filtering.
#
# Read perform_create and perform_update because those hooks are where the
# view adds fields that should not be trusted directly from serializer output.
#
# ============================================================
# END OF REVIEW
# ============================================================
