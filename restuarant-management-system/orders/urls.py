from django.urls import path

from .views import (
    OrderDetailView,
    OrderListCreateView,
    OrderStatusUpdateView,
)

app_name = 'orders'

urlpatterns = [
    path(
        'orders/',
        OrderListCreateView.as_view(),
        name='order-list-create',
    ),
    path(
        'orders/<int:pk>/',
        OrderDetailView.as_view(),
        name='order-detail',
    ),
    path(
        'orders/<int:pk>/status/',
        OrderStatusUpdateView.as_view(),
        name='order-status-update',
    ),
]
# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# app_name names this URL module as "orders" for namespaced reversing.
#
# order_collection_view sends POST requests to OrderCreateView and all other
# requests to OrderListView. This keeps GET and POST on /api/orders/ while
# preserving the separate view classes.
#
# urlpatterns maps order collection, order detail, and order status update
# endpoints to their views.
#
# Important decisions that were made and why
#
# The status update endpoint has its own path because staff should update only
# the status through that workflow.
#
# The collection URL handles both list and create because that is the normal
# REST pattern for a resource collection.
#
# What you should read and understand before you review the code
#
# Read Django path converters such as <int:pk>.
#
# Read why list/create endpoints often share the same collection URL.
#
# ============================================================
# END OF REVIEW
# ============================================================
