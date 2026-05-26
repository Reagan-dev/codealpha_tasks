from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from orders.models import Order, OrderItem


def get_daily_sales_report(date=None):
    """Return sales totals and top menu items for one calendar date."""
    report_date = date or timezone.localdate()
    served_orders = Order.objects.filter(
        status=Order.Status.SERVED,
        created_at__date=report_date,
    )
    total_orders = served_orders.count()
    total_revenue = (
        served_orders.aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0.00")
    )
    top_items = (
        OrderItem.objects.filter(order__in=served_orders)
        .values("menu_item__name")
        .annotate(total_quantity_sold=Sum("quantity"))
        .order_by("-total_quantity_sold", "menu_item__name")[:5]
    )
    average_order_value = (
        total_revenue / total_orders
        if total_orders
        else Decimal("0.00")
    )

    return {
        "date": str(report_date),
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "top_5_items": [
            {
                "menu_item": item["menu_item__name"],
                "total_quantity_sold": item["total_quantity_sold"],
            }
            for item in top_items
        ],
        "average_order_value": average_order_value,
    }


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# get_daily_sales_report returns a sales summary for one date.
#
# If no date is provided, it uses timezone.localdate so the report is based on
# Django's configured timezone instead of the server's raw system date.
#
# served_orders selects only orders with status SERVED for the requested date.
# This keeps cancelled, pending, and in-progress orders out of revenue reports.
#
# total_orders counts the served orders for that day.
#
# total_revenue sums total_amount from those served orders. If there are no
# matching orders, it returns Decimal("0.00") instead of None.
#
# top_items groups sold order items by menu item name, sums the quantities, and
# returns the five highest-selling items.
#
# average_order_value divides total revenue by total orders. It returns zero
# when there are no orders so the function never crashes from division by zero.
#
# Important decisions that were made and why
#
# The function returns a plain dictionary because reports are usually consumed
# by API views, dashboards, or management commands.
#
# Decimal is used for money values so totals and averages stay precise.
#
# The top item query uses values and annotate so the database does the grouping
# and summing efficiently.
#
# What you should read and understand before you review the code
#
# Read Django aggregation with Sum.
#
# Read values and annotate for grouped query results.
#
# Read timezone.localdate and created_at__date filtering.
#
# ============================================================
# END OF REVIEW
# ============================================================
