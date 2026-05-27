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
