from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique category name used to group similar events.",
    )
    description = models.TextField(
        help_text="Detailed explanation of what this category contains.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when this category was created.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    title = models.CharField(
        max_length=255,
        help_text="Public title of the event.",
    )
    description = models.TextField(
        help_text="Full details about the event.",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="events",
        help_text="Category this event belongs to.",
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="organized_events",
        help_text="User responsible for creating and managing this event.",
    )
    location = models.CharField(
        max_length=255,
        help_text="Physical or online location where the event will happen.",
    )
    start_datetime = models.DateTimeField(
        help_text="Date and time when the event starts.",
    )
    end_datetime = models.DateTimeField(
        help_text="Date and time when the event ends.",
    )
    capacity = models.PositiveIntegerField(
        help_text="Maximum number of confirmed registrations allowed.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PUBLISHED,
        help_text="Current publication and lifecycle status of the event.",
    )
    image = models.ImageField(
        upload_to="events/images/",
        null=True,
        blank=True,
        help_text="Optional image used to represent the event.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when this event was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when this event was last updated.",
    )

    class Meta:
        ordering = ["start_datetime"]
        verbose_name = "event"
        verbose_name_plural = "events"

    @property
    def current_registrations(self):
        return self.registrations.filter(
            status=Registration.Status.CONFIRMED,
        ).count()

    @property
    def is_full(self):
        return self.current_registrations >= self.capacity

    @property
    def spots_left(self):
        return self.capacity - self.current_registrations

    def __str__(self):
        return self.title


class Registration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        WAITLISTED = "WAITLISTED", "Waitlisted"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
        help_text="Event that the user registered for.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations",
        help_text="User who registered for the event.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
        help_text="Current status of this registration.",
    )
    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique ticket identifier for this registration.",
    )
    registered_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the user registered.",
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the registration was cancelled.",
    )

    class Meta:
        ordering = ["-registered_at"]
        unique_together = ["event", "user"]
        verbose_name = "registration"
        verbose_name_plural = "registrations"

    def __str__(self):
        return f"{self.user.email} — {self.event.title}"


