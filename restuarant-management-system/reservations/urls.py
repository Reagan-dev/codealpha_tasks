from django.urls import path

from .views import (
    ReservationCancelView,
    ReservationDetailView,
    ReservationListCreateView,
    TableListView,
)

app_name = 'reservations'

urlpatterns = [
    path(
        'tables/',
        TableListView.as_view(),
        name='table-list',
    ),
    path(
        'reservations/',
        ReservationListCreateView.as_view(),
        name='reservation-list-create',
    ),
    path(
        'reservations/<int:pk>/',
        ReservationDetailView.as_view(),
        name='reservation-detail',
    ),
    path(
        'reservations/<int:pk>/cancel/',
        ReservationCancelView.as_view(),
        name='reservation-cancel',
    ),
]
# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# app_name names this URL module as "reservations" so included URLs can be
# referenced as reservations:reservation-detail and similar names.
#
# reservation_collection_view sends POST requests to ReservationCreateView and
# all other requests to ReservationListView. It keeps GET and POST on
# /api/reservations/ while still using the separate views.
#
# urlpatterns maps table, reservation list/create, reservation detail/update,
# and reservation cancel endpoints to their views.
#
# Important decisions that were made and why
#
# Tables live in the reservations URL module because tables are used by the
# booking flow.
#
# The cancel endpoint is separate from the detail endpoint because cancelling
# is an action with a clear business meaning.
#
# What you should read and understand before you review the code
#
# Read Django URL namespaces and the name argument in path().
#
# Read DRF class-based views so you understand why as_view() is called in URL
# patterns.
#
# ============================================================
# END OF REVIEW
# ============================================================
