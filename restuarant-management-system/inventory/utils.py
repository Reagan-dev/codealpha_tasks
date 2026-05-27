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


