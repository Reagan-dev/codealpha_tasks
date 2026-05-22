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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# This file does not define custom classes or functions. It defines URL
# patterns that connect event and registration API paths to their views.
#
# CategoryListView is connected to /api/categories/ so clients can list event
# categories.
#
# EventListView is connected to /api/events/ so clients can browse events.
#
# EventCreateView is connected to /api/events/create/ so organizers can create
# events.
#
# EventDetailView is connected to /api/events/<pk>/ so clients can view one
# public event.
#
# EventUpdateView is connected to /api/events/<pk>/manage/ so organizers can
# view, edit, or delete events they own.
#
# RegistrationListView is connected to /api/registrations/ so users can view
# their own registrations.
#
# RegistrationCreateView is connected to /api/registrations/create/ so users can
# register for an event.
#
# RegistrationCancelView is connected to /api/registrations/<pk>/cancel/ so
# users can cancel their own registrations.
#
# Important decisions that were made and why
#
# app_name = "events" gives these routes a namespace and avoids route-name
# conflicts with other apps.
#
# Every path has a descriptive name so tests and other code can use reverse()
# instead of hard-coded URL strings.
#
# Create endpoints use /create/ paths so they do not conflict with list
# endpoints that use the same base resource path.
#
# What you should read and understand before you review the code
#
# Read Django path converters, especially <int:pk>.
#
# Read URL names and app namespaces.
#
# Read how DRF class-based views are connected with as_view().
#
# ============================================================
# END OF REVIEW
# ============================================================
