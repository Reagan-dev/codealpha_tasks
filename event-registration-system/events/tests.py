from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Event, Registration
from .utils import generate_ticket_number


User = get_user_model()


def create_user(email, username, role="MEMBER"):
    """Create a test user with the requested role."""
    return User.objects.create_user(
        email=email,
        username=username,
        password="StrongPass123!",
        role=role,
    )


def create_event(
    category,
    organizer,
    title="Test Event",
    capacity=10,
    start_offset=1,
    status_value=Event.Status.PUBLISHED,
):
    """Create a test event with sensible default values."""
    start_datetime = timezone.now() + timedelta(days=start_offset)

    return Event.objects.create(
        title=title,
        description=f"{title} description",
        category=category,
        organizer=organizer,
        location="Online",
        start_datetime=start_datetime,
        end_datetime=start_datetime + timedelta(hours=2),
        capacity=capacity,
        status=status_value,
    )


class CategoryModelTest(APITestCase):
    def test_category_creation(self):
        """Test that a category can be created successfully."""
        category = Category.objects.create(
            name="Technology",
            description="Technology events.",
        )

        self.assertEqual(category.name, "Technology")
        self.assertEqual(category.description, "Technology events.")

    def test_category_string_representation(self):
        """Test that a category returns its name as a string."""
        category = Category.objects.create(
            name="Business",
            description="Business events.",
        )

        self.assertEqual(str(category), "Business")


class EventModelTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Create shared model data for event property tests."""
        cls.organizer = create_user(
            email="organizer-model@example.com",
            username="organizermodel",
            role="ORGANIZER",
        )
        cls.member = create_user(
            email="member-model@example.com",
            username="membermodel",
        )
        cls.category = Category.objects.create(
            name="Model Category",
            description="Category for model tests.",
        )

    def test_spots_left_calculation(self):
        """Test that spots_left subtracts confirmed registrations."""
        event = create_event(
            category=self.category,
            organizer=self.organizer,
            title="Spots Left Event",
            capacity=3,
        )
        Registration.objects.create(
            event=event,
            user=self.member,
            ticket_number=generate_ticket_number(),
        )

        self.assertEqual(event.spots_left, 2)

    def test_is_full_when_at_capacity(self):
        """Test that is_full is True when capacity is reached."""
        event = create_event(
            category=self.category,
            organizer=self.organizer,
            title="Full Event",
            capacity=1,
        )
        Registration.objects.create(
            event=event,
            user=self.member,
            ticket_number=generate_ticket_number(),
        )

        self.assertTrue(event.is_full)

    def test_is_full_when_below_capacity(self):
        """Test that is_full is False when capacity remains."""
        event = create_event(
            category=self.category,
            organizer=self.organizer,
            title="Available Event",
            capacity=2,
        )
        Registration.objects.create(
            event=event,
            user=self.member,
            ticket_number=generate_ticket_number(),
        )

        self.assertFalse(event.is_full)


class RegistrationModelTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Create shared model data for registration constraint tests."""
        cls.organizer = create_user(
            email="organizer-registration@example.com",
            username="organizerregistration",
            role="ORGANIZER",
        )
        cls.member = create_user(
            email="member-registration@example.com",
            username="memberregistration",
        )
        cls.category = Category.objects.create(
            name="Registration Category",
            description="Category for registration tests.",
        )
        cls.event = create_event(
            category=cls.category,
            organizer=cls.organizer,
            title="Registration Constraint Event",
        )

    def test_duplicate_event_user_registration_raises_integrity_error(self):
        """Test that a user cannot register twice for the same event."""
        Registration.objects.create(
            event=self.event,
            user=self.member,
            ticket_number=generate_ticket_number(),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Registration.objects.create(
                    event=self.event,
                    user=self.member,
                    ticket_number=generate_ticket_number(),
                )


class RegisterViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Create an existing user for duplicate registration tests."""
        cls.url = reverse("accounts:register")
        cls.existing_user = create_user(
            email="existing@example.com",
            username="existinguser",
        )

    def test_successful_registration(self):
        """Test that a new user can register successfully."""
        response = self.client.post(
            self.url,
            {
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
                "role": "MEMBER",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(email="newuser@example.com").exists(),
        )

    def test_duplicate_email_returns_400(self):
        """Test that registration fails when email already exists."""
        response = self.client.post(
            self.url,
            {
                "email": self.existing_user.email,
                "username": "duplicateuser",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
                "role": "MEMBER",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_mismatch_returns_400(self):
        """Test that registration fails when passwords do not match."""
        response = self.client.post(
            self.url,
            {
                "email": "mismatch@example.com",
                "username": "mismatchuser",
                "password": "StrongPass123!",
                "password2": "DifferentPass123!",
                "role": "MEMBER",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EventListViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Create shared events for list filtering tests."""
        cls.url = reverse("events:event_list")
        cls.organizer = create_user(
            email="organizer-list@example.com",
            username="organizerlist",
            role="ORGANIZER",
        )
        cls.tech_category = Category.objects.create(
            name="Tech",
            description="Technology category.",
        )
        cls.business_category = Category.objects.create(
            name="Business List",
            description="Business category.",
        )
        cls.published_event = create_event(
            category=cls.tech_category,
            organizer=cls.organizer,
            title="Published Tech Event",
            status_value=Event.Status.PUBLISHED,
        )
        cls.business_event = create_event(
            category=cls.business_category,
            organizer=cls.organizer,
            title="Business Event",
            status_value=Event.Status.PUBLISHED,
        )
        cls.past_event = create_event(
            category=cls.tech_category,
            organizer=cls.organizer,
            title="Past Event",
            start_offset=-2,
            status_value=Event.Status.PUBLISHED,
        )

    def test_lists_published_events(self):
        """Test that the event list returns published events."""
        response = self.client.get(self.url)
        titles = [event["title"] for event in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.published_event.title, titles)

    def test_filter_by_category(self):
        """Test that events can be filtered by category ID."""
        response = self.client.get(
            self.url,
            {"category": self.business_category.pk},
        )
        titles = [event["title"] for event in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.business_event.title, titles)
        self.assertNotIn(self.published_event.title, titles)

    def test_upcoming_filter(self):
        """Test that upcoming=true returns only future events."""
        response = self.client.get(self.url, {"upcoming": "true"})
        titles = [event["title"] for event in response.data["results"]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.published_event.title, titles)
        self.assertNotIn(self.past_event.title, titles)


class EventCreateViewTest(APITestCase):
    def setUp(self):
        """Create organizer, member, category, and request payload."""
        self.url = reverse("events:event_create")
        self.organizer = create_user(
            email="organizer-create@example.com",
            username="organizercreate",
            role="ORGANIZER",
        )
        self.member = create_user(
            email="member-create@example.com",
            username="membercreate",
        )
        self.category = Category.objects.create(
            name="Create Category",
            description="Category for create tests.",
        )
        start_datetime = timezone.now() + timedelta(days=5)
        self.payload = {
            "title": "Created Event",
            "description": "Created event description.",
            "category": self.category.pk,
            "location": "Online",
            "start_datetime": start_datetime.isoformat(),
            "end_datetime": (start_datetime + timedelta(hours=2)).isoformat(),
            "capacity": 20,
            "status": Event.Status.PUBLISHED,
        }

    def test_organizer_can_create_event(self):
        """Test that an organizer can create an event."""
        self.client.force_authenticate(user=self.organizer)
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Event.objects.filter(
                title="Created Event",
                organizer=self.organizer,
            ).exists(),
        )

    def test_member_cannot_create_event(self):
        """Test that a member cannot create an event."""
        self.client.force_authenticate(user=self.member)
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_event(self):
        """Test that unauthenticated users cannot create events."""
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RegistrationCreateViewTest(APITestCase):
    def setUp(self):
        """Create users and events for registration creation tests."""
        self.url = reverse("events:registration_create")
        self.organizer = create_user(
            email="organizer-reg-create@example.com",
            username="organizerregcreate",
            role="ORGANIZER",
        )
        self.member = create_user(
            email="member-reg-create@example.com",
            username="memberregcreate",
        )
        self.second_member = create_user(
            email="member-reg-second@example.com",
            username="memberregsecond",
        )
        self.category = Category.objects.create(
            name="Registration Create Category",
            description="Category for registration create tests.",
        )
        self.event = create_event(
            category=self.category,
            organizer=self.organizer,
            title="Registration Create Event",
            capacity=5,
        )

    def test_member_can_register_for_event(self):
        """Test that an authenticated member can register for an event."""
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            self.url,
            {"event": self.event.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Registration.objects.filter(
                event=self.event,
                user=self.member,
            ).exists(),
        )

    def test_registration_returns_ticket_number(self):
        """Test that a registration response includes a ticket number."""
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            self.url,
            {"event": self.event.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("ticket_number", response.data)
        self.assertTrue(response.data["ticket_number"].startswith("TKT-"))

    def test_duplicate_registration_returns_400(self):
        """Test that duplicate event registration returns a 400 response."""
        Registration.objects.create(
            event=self.event,
            user=self.member,
            ticket_number=generate_ticket_number(),
        )
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            self.url,
            {"event": self.event.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_on_full_event_returns_waitlisted_status(self):
        """Test that full events create waitlisted registrations."""
        full_event = create_event(
            category=self.category,
            organizer=self.organizer,
            title="Full Registration Event",
            capacity=1,
        )
        Registration.objects.create(
            event=full_event,
            user=self.second_member,
            ticket_number=generate_ticket_number(),
        )
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            self.url,
            {"event": full_event.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Registration.Status.WAITLISTED)


class RegistrationCancelViewTest(APITestCase):
    def setUp(self):
        """Create users, event, and registrations for cancellation tests."""
        self.organizer = create_user(
            email="organizer-cancel@example.com",
            username="organizercancel",
            role="ORGANIZER",
        )
        self.member = create_user(
            email="member-cancel@example.com",
            username="membercancel",
        )
        self.waitlisted_member = create_user(
            email="waitlisted-cancel@example.com",
            username="waitlistedcancel",
        )
        self.category = Category.objects.create(
            name="Cancel Category",
            description="Category for cancellation tests.",
        )
        self.event = create_event(
            category=self.category,
            organizer=self.organizer,
            title="Cancellation Event",
            capacity=1,
        )

    def test_user_can_cancel_own_registration(self):
        """Test that a user can cancel their own registration."""
        registration = Registration.objects.create(
            event=self.event,
            user=self.member,
            ticket_number=generate_ticket_number(),
        )
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            reverse(
                "events:registration_cancel",
                kwargs={"pk": registration.pk},
            ),
        )
        registration.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(registration.status, Registration.Status.CANCELLED)
        self.assertIsNotNone(registration.cancelled_at)

    def test_cancelling_confirms_next_waitlisted_user(self):
        """Test that cancellation promotes the oldest waitlisted user."""
        registration = Registration.objects.create(
            event=self.event,
            user=self.member,
            ticket_number=generate_ticket_number(),
        )
        waitlisted_registration = Registration.objects.create(
            event=self.event,
            user=self.waitlisted_member,
            status=Registration.Status.WAITLISTED,
            ticket_number=generate_ticket_number(),
        )
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            reverse(
                "events:registration_cancel",
                kwargs={"pk": registration.pk},
            ),
        )
        waitlisted_registration.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            waitlisted_registration.status,
            Registration.Status.CONFIRMED,
        )


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# create_user is a small test helper. It creates users with a default password
# and role so each test does not repeat the same setup code.
#
# create_event is another test helper. It creates events with valid dates,
# category, organizer, capacity, and status.
#
# CategoryModelTest checks that categories can be created and that __str__
# returns the category name.
#
# EventModelTest checks Event properties. spots_left must subtract confirmed
# registrations from capacity. is_full must be True at capacity and False below
# capacity.
#
# RegistrationModelTest checks the unique_together database rule. It proves the
# same user cannot register for the same event twice.
#
# RegisterViewTest checks registration API behavior: successful signup,
# duplicate email validation, and password confirmation validation.
#
# EventListViewTest checks the public event list endpoint and its filters.
#
# EventCreateViewTest checks role-based access: organizers can create events,
# members cannot, and unauthenticated users cannot.
#
# RegistrationCreateViewTest checks registration creation, ticket number output,
# duplicate registration protection, and waitlisting when an event is full.
#
# RegistrationCancelViewTest checks that users can cancel their own
# registrations and that the next waitlisted registration is promoted.
#
# Important decisions that were made and why
#
# APITestCase is used for both model and API tests so the whole file has one
# consistent test base and API client support is available where needed.
#
# setUpTestData is used when shared class data is safe to reuse across tests.
# setUp is used when each test needs fresh objects that may be changed.
#
# reverse() is used for URLs so tests stay correct if path strings change but
# URL names stay the same.
#
# force_authenticate is used to test permissions without depending on JWT token
# setup in every test.
#
# transaction.atomic is used around the duplicate registration check so the
# IntegrityError does not break the outer test transaction.
#
# What you should read and understand before you review the code
#
# Read Django TestCase and DRF APITestCase.
#
# Read reverse() and named URLs.
#
# Read force_authenticate in DRF tests.
#
# Read database IntegrityError and unique_together constraints.
#
# Read the registration create and cancel view logic before reviewing the API
# tests.
#
# ============================================================
# END OF REVIEW
# ============================================================
