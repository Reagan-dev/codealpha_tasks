from rest_framework import serializers

from .models import Category, Event, Registration
from .utils import generate_ticket_number


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class EventListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    organizer_email = serializers.EmailField(
        source="organizer.email",
        read_only=True,
    )
    spots_left = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "category_name",
            "organizer_email",
            "location",
            "start_datetime",
            "capacity",
            "spots_left",
            "is_full",
            "status",
            "image",
        )


class EventDetailSerializer(EventListSerializer):
    class Meta(EventListSerializer.Meta):
        fields = EventListSerializer.Meta.fields + (
            "description",
            "end_datetime",
            "created_at",
        )


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    organizer = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Event
        fields = (
            "title",
            "description",
            "category",
            "organizer",
            "location",
            "start_datetime",
            "end_datetime",
            "capacity",
            "status",
            "image",
        )

    def validate(self, attrs):
        """Validate event timing and capacity rules."""
        start_datetime = attrs.get("start_datetime")
        end_datetime = attrs.get("end_datetime")
        capacity = attrs.get("capacity")

        if self.instance:
            start_datetime = start_datetime or self.instance.start_datetime
            end_datetime = end_datetime or self.instance.end_datetime
            capacity = capacity if capacity is not None else self.instance.capacity

        if start_datetime and end_datetime:
            if end_datetime <= start_datetime:
                raise serializers.ValidationError(
                    {
                        "end_datetime": (
                            "End datetime must be after start datetime."
                        ),
                    },
                )

        if capacity is not None and capacity <= 0:
            raise serializers.ValidationError(
                {"capacity": "Capacity must be greater than 0."},
            )

        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(),
    )

    class Meta:
        model = Registration
        fields = (
            "event",
            "ticket_number",
            "status",
            "registered_at",
        )
        read_only_fields = (
            "ticket_number",
            "status",
            "registered_at",
        )

    def create(self, validated_data):
        """Create a registration for the authenticated user."""
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required to register for an event.",
            )

        return Registration.objects.create(
            user=request.user,
            ticket_number=generate_ticket_number(),
            **validated_data,
        )


class RegistrationDetailSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(
        source="event.title",
        read_only=True,
    )
    start_datetime = serializers.DateTimeField(
        source="event.start_datetime",
        read_only=True,
    )
    location = serializers.CharField(
        source="event.location",
        read_only=True,
    )

    class Meta:
        model = Registration
        fields = (
            "event_title",
            "start_datetime",
            "location",
            "ticket_number",
            "status",
            "registered_at",
            "cancelled_at",
        )


