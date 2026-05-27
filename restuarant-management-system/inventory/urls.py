from django.urls import path

from .views import (
    DailySalesReportView,
    InventoryListView,
    InventoryRestockView,
)


app_name = "inventory"


urlpatterns = [
    path(
        "inventory/",
        InventoryListView.as_view(),
        name="inventory-list",
    ),
    path(
        "inventory/<int:pk>/restock/",
        InventoryRestockView.as_view(),
        name="inventory-restock",
    ),
    path(
        "reports/daily-sales/",
        DailySalesReportView.as_view(),
        name="daily-sales-report",
    ),
]



