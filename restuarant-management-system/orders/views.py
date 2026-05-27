from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission, IsAuthenticated

from core.permissions import IsOrderOwner, IsStaff

from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderStatusUpdateSerializer,
)


class IsOrderOwnerOrStaff(BasePermission):
    """Allow order owners or staff users to access an order object."""

    def has_object_permission(self, request, view, obj):
        return (
            IsOrderOwner().has_object_permission(request, view, obj)
            or IsStaff().has_permission(request, view)
        )


class OrderCreateView(generics.CreateAPIView):
    """Create an order for the authenticated user."""

    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = (IsAuthenticated,)


class OrderDetailView(generics.RetrieveAPIView):
    """Return one order for its owner or for staff."""

    queryset = Order.objects.select_related(
        "customer",
        "table",
    ).prefetch_related("items__menu_item")
    serializer_class = OrderDetailSerializer
    permission_classes = (IsAuthenticated, IsOrderOwnerOrStaff)


class OrderStatusUpdateView(generics.UpdateAPIView):
    """Update an order status."""

    http_method_names = ("patch", "head", "options")
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = (IsStaff,)


class OrderListView(generics.ListAPIView):
    """Return all orders for staff, optionally filtered by status."""

    serializer_class = OrderDetailSerializer
    permission_classes = (IsStaff,)

    def get_queryset(self):
        queryset = Order.objects.select_related(
            "customer",
            "table",
        ).prefetch_related("items__menu_item")
        order_status = self.request.query_params.get("status")

        if order_status:
            if order_status not in Order.Status.values:
                raise ValidationError(
                    {"status": "Use a valid order status."}
                )

            queryset = queryset.filter(status=order_status)

        return queryset
    
from rest_framework.generics import ListCreateAPIView


class OrderListCreateView(ListCreateAPIView):
    """
    GET  /api/orders/ — list all orders, staff only, filter by ?status=
    POST /api/orders/ — create an order, any authenticated user.
    """

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [IsStaff()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderDetailSerializer

    def get_queryset(self):
        queryset = Order.objects.select_related(
            'customer',
            'table',
        ).prefetch_related('items__menu_item')

        order_status = self.request.query_params.get('status')

        if order_status:
            if order_status not in Order.Status.values:
                raise ValidationError(
                    {'status': 'Use a valid order status.'}
                )
            queryset = queryset.filter(status=order_status)

        return queryset


