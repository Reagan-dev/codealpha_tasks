from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status as response_status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Category, Event, Registration
from .permissions import IsEventOrganizer, IsOrganizer, IsRegistrationOwner
from .serializers import (
    CategorySerializer,
    EventCreateUpdateSerializer,
    EventDetailSerializer,
    EventListSerializer,
    RegistrationDetailSerializer,
    RegistrationSerializer,
)
from .utils import (
    generate_ticket_number,
    send_cancellation_email,
    send_registration_email,
)


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)


class EventListView(ListAPIView):
    serializer_class = EventListSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Return events filtered by query parameters."""
        queryset = Event.objects.select_related(
            "category",
            "organizer",
        ).all()
        category = self.request.query_params.get("category")
        event_status = self.request.query_params.get("status")
        search = self.request.query_params.get("search")
        upcoming = self.request.query_params.get("upcoming")

        if category:
            if category.isdigit():
                queryset = queryset.filter(category_id=category)
            else:
                queryset = queryset.filter(category__name__iexact=category)

        if event_status:
            queryset = queryset.filter(status=event_status)
        else:
            queryset = queryset.exclude(status=Event.Status.DRAFT)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search),
            )

        if str(upcoming).lower() in {"1", "true", "yes"}:
            queryset = queryset.filter(start_datetime__gte=timezone.now())

        return queryset


class EventDetailView(RetrieveAPIView):
    queryset = Event.objects.select_related("category", "organizer").all()
    serializer_class = EventDetailSerializer
    permission_classes = (AllowAny,)


class EventCreateView(CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventCreateUpdateSerializer
    permission_classes = (IsOrganizer,)

    def perform_create(self, serializer):
        """Create an event for the authenticated organizer."""
        serializer.save(organizer=self.request.user)


class EventUpdateView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.select_related("category", "organizer").all()
    serializer_class = EventCreateUpdateSerializer
    permission_classes = (IsOrganizer, IsEventOrganizer)


class RegistrationCreateView(CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """Create a registration or waitlist entry for an event."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.validated_data["event"]

        with transaction.atomic():
            event = Event.objects.select_for_update().get(pk=event.pk)

            if Registration.objects.filter(
                event=event,
                user=request.user,
            ).exists():
                return Response(
                    {
                        "detail": (
                            "You are already registered for this event."
                        ),
                    },
                    status=response_status.HTTP_400_BAD_REQUEST,
                )

            registration_status = Registration.Status.CONFIRMED

            if event.is_full:
                registration_status = Registration.Status.WAITLISTED

            registration = Registration.objects.create(
                event=event,
                user=request.user,
                status=registration_status,
                ticket_number=generate_ticket_number(),
            )

        send_registration_email(request.user, registration, event)

        response_serializer = RegistrationDetailSerializer(
            registration,
            context=self.get_serializer_context(),
        )
        return Response(
            response_serializer.data,
            status=response_status.HTTP_201_CREATED,
        )


class RegistrationListView(ListAPIView):
    serializer_class = RegistrationDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return registrations owned by the authenticated user."""
        return Registration.objects.select_related("event", "user").filter(
            user=self.request.user,
        )


class RegistrationCancelView(UpdateAPIView):
    queryset = Registration.objects.select_related("event", "user").all()
    serializer_class = RegistrationDetailSerializer
    permission_classes = (IsAuthenticated, IsRegistrationOwner)
    http_method_names = ("post", "options", "head")

    def post(self, request, *args, **kwargs):
        """Cancel a registration and promote the next waitlisted user."""
        registration = self.get_object()

        with transaction.atomic():
            registration = Registration.objects.select_for_update().get(
                pk=registration.pk,
            )
            self.check_object_permissions(request, registration)

            if registration.status == Registration.Status.CANCELLED:
                return Response(
                    {"detail": "This registration is already cancelled."},
                    status=response_status.HTTP_400_BAD_REQUEST,
                )

            event = Event.objects.select_for_update().get(
                pk=registration.event_id,
            )
            registration.status = Registration.Status.CANCELLED
            registration.cancelled_at = timezone.now()
            registration.save(
                update_fields=(
                    "status",
                    "cancelled_at",
                ),
            )

            next_registration = (
                Registration.objects.select_for_update()
                .filter(
                    event=event,
                    status=Registration.Status.WAITLISTED,
                )
                .order_by("registered_at")
                .first()
            )

            if next_registration and not event.is_full:
                next_registration.status = Registration.Status.CONFIRMED
                next_registration.save(update_fields=("status",))

        send_cancellation_email(request.user, event)

        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=response_status.HTTP_200_OK)


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# CategoryListView handles GET /api/categories/. It is public because users
# should be able to see event categories before logging in.
#
# EventListView handles GET /api/events/. It returns public event list data and
# supports category, status, search, and upcoming query parameters.
#
# EventListView.get_queryset builds the filtered event query. It searches title
# and description, excludes draft events by default, filters future events when
# upcoming=true, and supports category by ID or exact category name.
#
# EventDetailView handles GET /api/events/<pk>/. It returns more information
# about one event than the list endpoint.
#
# EventCreateView handles POST /api/events/. It requires the organizer role and
# saves the logged-in user as the event organizer.
#
# EventUpdateView handles GET, PATCH, and DELETE /api/events/<pk>/manage/. It
# requires the user to be an organizer and also the organizer of that specific
# event.
#
# RegistrationCreateView handles POST /api/registrations/. It checks duplicate
# registrations, creates a confirmed registration when seats are available, and
# creates a waitlisted registration when the event is full.
#
# RegistrationListView handles GET /api/registrations/. It returns only the
# logged-in user's registrations.
#
# RegistrationCancelView handles POST /api/registrations/<pk>/cancel/. It marks
# the registration as cancelled, stores cancelled_at, sends a cancellation
# email, and promotes the oldest waitlisted registration if a confirmed spot is
# available.
#
# Important decisions that were made and why
#
# Registration creation is implemented in the view instead of relying only on
# the serializer because it has business rules: duplicate checks, full-event
# checks, waitlisting, ticket generation, and email sending.
#
# select_for_update and transaction.atomic are used around registration changes
# to reduce race conditions when multiple users register or cancel at the same
# time.
#
# RegistrationCancelView accepts POST because cancelling is an action, not a
# normal partial update form.
#
# EventCreateView sets organizer from request.user so clients cannot create an
# event for another organizer.
#
# What you should read and understand before you review the code
#
# Read DRF generic views: ListAPIView, RetrieveAPIView, CreateAPIView,
# RetrieveUpdateDestroyAPIView, and UpdateAPIView.
#
# Read DRF permission_classes and object permissions.
#
# Read Django query filtering with Q objects.
#
# Read transaction.atomic and select_for_update so you understand why they are
# used around registration and cancellation.
#
# Read DRF Response and HTTP status codes.
#
# ============================================================
# END OF REVIEW
# ============================================================
