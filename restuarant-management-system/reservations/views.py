from datetime import timedelta

from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsReservationOwner

from .models import Reservation, RestaurantTable
from .serializers import (
    ReservationCreateSerializer,
    ReservationDetailSerializer,
    RestaurantTableSerializer,
)


class ReservationUpdateSerializer(ReservationCreateSerializer):
    """Validate reservation updates while keeping unchanged instance values."""

    def validate(self, attrs):
        table = attrs.get("table", self.instance.table)
        party_size = attrs.get("party_size", self.instance.party_size)
        starts_at = attrs.get(
            "reservation_datetime",
            self.instance.reservation_datetime,
        )
        duration_minutes = attrs.get(
            "duration_minutes",
            self.instance.duration_minutes,
        )
        ends_at = starts_at + timedelta(minutes=duration_minutes)

        if party_size > table.capacity:
            raise self.validation_error(
                "party_size",
                "Party size cannot be greater than table capacity.",
            )

        if self._has_conflicting_reservation(table, starts_at, ends_at):
            raise self.validation_error(
                "reservation_datetime",
                "This table already has a conflicting reservation.",
            )

        return attrs

    def _has_conflicting_reservation(self, table, starts_at, ends_at):
        reservations = Reservation.objects.filter(table=table).exclude(
            status__in=(
                Reservation.Status.CANCELLED,
                Reservation.Status.COMPLETED,
            )
        )
        reservations = reservations.exclude(pk=self.instance.pk)

        for reservation in reservations:
            existing_starts_at = reservation.reservation_datetime
            existing_ends_at = existing_starts_at + timedelta(
                minutes=reservation.duration_minutes
            )

            if existing_starts_at < ends_at and existing_ends_at > starts_at:
                return True

        return False

    @staticmethod
    def validation_error(field, message):
        return serializers.ValidationError({field: message})


class TableListView(generics.ListAPIView):
    """Return active restaurant tables."""

    queryset = RestaurantTable.objects.filter(is_active=True)
    serializer_class = RestaurantTableSerializer
    permission_classes = (AllowAny,)


class ReservationCreateView(generics.CreateAPIView):
    """Create a reservation for the authenticated user."""

    queryset = Reservation.objects.select_related("table", "customer")
    serializer_class = ReservationCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class ReservationListView(generics.ListAPIView):
    """Return reservations owned by the authenticated user."""

    serializer_class = ReservationDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Reservation.objects.select_related("table", "customer").filter(
            customer=self.request.user
        )


class ReservationDetailView(generics.RetrieveUpdateAPIView):
    """Return or update one reservation owned by the authenticated user."""

    http_method_names = ("get", "patch", "head", "options")
    queryset = Reservation.objects.select_related("table", "customer")
    permission_classes = (IsAuthenticated, IsReservationOwner)

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ReservationUpdateSerializer

        return ReservationDetailSerializer

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        serializer = ReservationDetailSerializer(
            self.get_object(),
            context=self.get_serializer_context(),
        )

        return Response(serializer.data)


class ReservationCancelView(APIView):
    """Cancel one reservation owned by the authenticated user."""

    permission_classes = (IsAuthenticated, IsReservationOwner)

    def post(self, request, pk):
        reservation = generics.get_object_or_404(
            Reservation.objects.select_related("table", "customer"),
            pk=pk,
        )
        self.check_object_permissions(request, reservation)
        reservation.status = Reservation.Status.CANCELLED
        reservation.save(update_fields=("status",))
        serializer = ReservationDetailSerializer(reservation)

        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# ReservationUpdateSerializer validates PATCH requests for reservations. It
# reuses the create serializer rules, but fills missing PATCH fields from the
# current reservation so partial updates can still be checked correctly.
#
# validate checks table capacity and time conflicts for the final reservation
# values after the patch is applied.
#
# _has_conflicting_reservation checks other active reservations for the same
# table and excludes the reservation currently being updated.
#
# validation_error creates a DRF validation error with a simple field-message
# shape.
#
# TableListView returns only active tables because inactive tables should not
# be shown for booking.
#
# ReservationCreateView creates a reservation and sets customer from
# request.user. This prevents clients from creating reservations for another
# user by changing request data.
#
# ReservationListView returns only the authenticated user's reservations.
#
# ReservationDetailView lets the owner read or patch one reservation.
#
# ReservationCancelView handles the cancel action and sets status to
# CANCELLED.
#
# Important decisions that were made and why
#
# IsReservationOwner is used on detail and cancel endpoints so users can only
# access their own reservations.
#
# PATCH returns ReservationDetailSerializer output so the response is the same
# detailed shape as the GET endpoint.
#
# Cancellation is a separate APIView because it is an action, not a normal
# field update from arbitrary request data.
#
# What you should read and understand before you review the code
#
# Read DRF object permissions and check_object_permissions.
#
# Read partial updates in RetrieveUpdateAPIView.
#
# Read why update endpoints often use a write serializer for input and a read
# serializer for output.
#
# ============================================================
# END OF REVIEW
# ============================================================
