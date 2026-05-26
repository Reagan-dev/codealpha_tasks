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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# app_name names this URL module as "inventory" for namespaced URL reversing.
#
# urlpatterns maps inventory listing, inventory restocking, and daily sales
# report URLs to their views.
#
# Important decisions that were made and why
#
# The daily sales report route is kept in inventory.urls because the report
# function lives in inventory.utils and reports are closely related to stock
# and sales tracking.
#
# Restocking has a separate action URL because it adds stock instead of
# replacing the entire inventory item.
#
# What you should read and understand before you review the code
#
# Read Django URL routing with path().
#
# Read namespaced URL reversing with app_name and namespace.
#
# ============================================================
# END OF REVIEW
# ============================================================
