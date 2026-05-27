from django.urls import path

from .views import (
    CategoryListView,
    EventCreateView,
    EventDetailView,
    EventListView,
    EventUpdateView,
    RegistrationCancelView,
    RegistrationCreateView,
    RegistrationListView,
)


app_name = "events"

urlpatterns = [
    path(
        "categories/",
        CategoryListView.as_view(),
        name="category_list",
    ),
    path(
        "events/",
        EventListView.as_view(),
        name="event_list",
    ),
    path(
        "events/create/",
        EventCreateView.as_view(),
        name="event_create",
    ),
    path(
        "events/<int:pk>/",
        EventDetailView.as_view(),
        name="event_detail",
    ),
    path(
        "events/<int:pk>/manage/",
        EventUpdateView.as_view(),
        name="event_manage",
    ),
    path(
        "registrations/",
        RegistrationListView.as_view(),
        name="registration_list",
    ),
    path(
        "registrations/create/",
        RegistrationCreateView.as_view(),
        name="registration_create",
    ),
    path(
        "registrations/<int:pk>/cancel/",
        RegistrationCancelView.as_view(),
        name="registration_cancel",
    ),
]



