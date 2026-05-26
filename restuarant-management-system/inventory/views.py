from django.db.models import F
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsManager, IsStaff

from .models import InventoryItem
from .serializers import InventoryItemSerializer, RestockSerializer
from .utils import get_daily_sales_report


class InventoryListView(generics.ListAPIView):
    """Return inventory items for staff."""

    serializer_class = InventoryItemSerializer
    permission_classes = (IsStaff,)

    def get_queryset(self):
        queryset = InventoryItem.objects.all()
        low_stock = self.request.query_params.get("low_stock")

        if low_stock is not None:
            low_stock = low_stock.lower()

            if low_stock == "true":
                queryset = queryset.filter(
                    quantity_in_stock__lte=F("reorder_level")
                )
            elif low_stock != "false":
                raise ValidationError(
                    {"low_stock": "Use true or false."}
                )

        return queryset


class InventoryRestockView(generics.UpdateAPIView):
    """Add stock to one inventory item."""

    http_method_names = ("patch", "head", "options")
    queryset = InventoryItem.objects.all()
    serializer_class = RestockSerializer
    permission_classes = (IsManager,)

    def update(self, request, *args, **kwargs):
        inventory_item = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity_to_add = serializer.validated_data["quantity_to_add"]
        inventory_item.quantity_in_stock += quantity_to_add
        inventory_item.last_restocked = timezone.now()
        inventory_item.save(
            update_fields=(
                "quantity_in_stock",
                "last_restocked",
                "updated_at",
            )
        )
        output_serializer = InventoryItemSerializer(inventory_item)

        return Response(output_serializer.data, status=status.HTTP_200_OK)


class DailySalesReportView(APIView):
    """Return the daily sales report for staff."""

    permission_classes = (IsStaff,)

    def get(self, request):
        date_value = request.query_params.get("date")

        if date_value:
            report_date = parse_date(date_value)

            if report_date is None:
                raise ValidationError(
                    {"date": "Use YYYY-MM-DD format."}
                )
        else:
            report_date = None

        return Response(get_daily_sales_report(report_date))


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# InventoryListView returns inventory items for staff users. It supports
# ?low_stock=true so staff can quickly see items at or below reorder level.
#
# get_queryset applies the low-stock filter at the database level with F()
# instead of loading every item into Python.
#
# InventoryRestockView adds a positive quantity to one inventory item. It uses
# RestockSerializer for validation and then returns the updated inventory item.
#
# update handles the restock action because RestockSerializer is an action
# serializer, not a normal model update serializer.
#
# DailySalesReportView returns the report dictionary from
# get_daily_sales_report. It optionally accepts ?date=YYYY-MM-DD.
#
# get validates the date query parameter before calling the report utility.
#
# Important decisions that were made and why
#
# Restocking requires IsManager because changing stock levels is a higher-risk
# action than viewing inventory.
#
# Daily sales reports require staff access because they expose business
# revenue and order totals.
#
# parse_date is used so invalid date strings are rejected clearly before the
# report query runs.
#
# What you should read and understand before you review the code
#
# Read Django F expressions for comparing or updating fields in the database.
#
# Read DRF APIView for action-style endpoints that do not map cleanly to a
# normal model serializer save.
#
# Read the get_daily_sales_report utility so you understand what the report
# endpoint returns.
#
# ============================================================
# END OF REVIEW
# ============================================================
