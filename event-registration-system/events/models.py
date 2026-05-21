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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# Category groups events by topic, such as technology, business, education, or
# sports. The name is unique so duplicate categories are not created.
#
# Category.__str__ returns the category name so the admin and shell display a
# readable value instead of "Category object".
#
# Event stores the main event information: title, description, category,
# organizer, location, start time, end time, capacity, status, optional image,
# and timestamps.
#
# Event.Status is a TextChoices class. It limits event status values to DRAFT,
# PUBLISHED, CANCELLED, and COMPLETED so event lifecycle logic stays consistent.
#
# Event.current_registrations counts only confirmed registrations. Cancelled
# and waitlisted records do not take confirmed seats.
#
# Event.is_full returns True when confirmed registrations are equal to or more
# than the event capacity. This helps views and serializers quickly decide if a
# new confirmed registration should be blocked or waitlisted.
#
# Event.spots_left returns capacity minus confirmed registrations. It gives the
# API a simple way to show how many confirmed places remain.
#
# Event.__str__ returns the title because that is the clearest label for an
# event in admin screens and logs.
#
# Registration connects a user to an event. It stores the registration status,
# ticket number, registration time, and optional cancellation time.
#
# Registration.Status is a TextChoices class. It keeps registration status
# values limited to CONFIRMED, CANCELLED, and WAITLISTED.
#
# Registration.__str__ returns "user.email — event.title" so each registration
# is easy to identify by both attendee and event.
#
# Important decisions that were made and why
#
# Event.organizer uses on_delete=PROTECT because deleting an organizer should
# not accidentally delete or orphan events they created.
#
# Event.category uses on_delete=CASCADE because if a category is deleted, its
# grouped events are removed too. If you want to preserve events after category
# deletion, use PROTECT instead.
#
# Registration uses unique_together for event and user so one user cannot
# register for the same event more than once.
#
# related_name values were added so reverse queries are clear, for example
# event.registrations.all() and user.organized_events.all().
#
# settings.AUTH_USER_MODEL is used instead of importing User directly. This is
# the recommended Django pattern when a project has a custom user model.
#
# spots_left can become negative if capacity is lowered below the current
# confirmed registration count. That is useful because it shows the event is
# over capacity instead of hiding the problem.
#
# What you should read and understand before you review the code
#
# Read Django model relationships, especially ForeignKey, related_name,
# on_delete=CASCADE, and on_delete=PROTECT.
#
# Read Django model Meta options, especially ordering, unique_together,
# verbose_name, and verbose_name_plural.
#
# Read Django model properties so you understand why current_registrations,
# is_full, and spots_left are accessed like fields but calculated in Python.
#
# Read ImageField requirements. You need Pillow installed for image uploads.
#
# Read database constraints so you understand why ticket_number is unique and
# why event plus user must be unique together.
#
# ============================================================
# END OF REVIEW
# ============================================================
