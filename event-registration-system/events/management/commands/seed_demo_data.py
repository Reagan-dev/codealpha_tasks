from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from events.models import Category, Event, Registration
from events.utils import generate_ticket_number


User = get_user_model()
PASSWORD = "TestPass123!"


class Command(BaseCommand):
    """Seed demo data for the Event Registration System."""

    help = "Seed demo users, categories, events, and registrations."

    def handle(self, *args, **options):
        self._configure_output()

        if Category.objects.exists():
            self.stdout.write(self.style.WARNING("Already seeded. Skipping."))
            return

        now = timezone.now()

        with transaction.atomic():
            organisers, organiser_count = self._create_organisers()
            members, member_count = self._create_members()
            categories, category_count = self._create_categories()
            events, event_count = self._create_events(
                organisers,
                categories,
                now,
            )
            registrations = self._create_registrations(members, events, now)

        self._print_summary(
            organiser_count,
            member_count,
            category_count,
            event_count,
            registrations,
        )

    def _configure_output(self):
        output_stream = getattr(self.stdout, "_out", None)

        if hasattr(output_stream, "reconfigure"):
            output_stream.reconfigure(encoding="utf-8")

    def _create_organisers(self):
        organiser_data = [
            {
                "email": "organizer1@example.com",
                "username": "events_ke",
                "first_name": "Sarah",
                "last_name": "Mwangi",
                "phone_number": "+254700000001",
                "bio": "Event curator based in Nairobi.",
            },
            {
                "email": "organizer2@example.com",
                "username": "techtalks",
                "first_name": "James",
                "last_name": "Ochieng",
                "phone_number": "+254700000002",
                "bio": "Tech community builder.",
            },
        ]
        organisers = {}
        created_count = 0

        for data in organiser_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "username": data["username"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "role": User.Role.ORGANIZER,
                    "phone_number": data["phone_number"],
                    "bio": data["bio"],
                },
            )

            if created:
                user.set_password(PASSWORD)
                user.save(update_fields=["password"])
                created_count += 1

            organisers[data["username"]] = user

        return organisers, created_count

    def _create_members(self):
        member_data = [
            {
                "email": "alice@example.com",
                "username": "alice_m",
                "first_name": "Alice",
                "last_name": "Kamau",
            },
            {
                "email": "bob@example.com",
                "username": "bob_o",
                "first_name": "Bob",
                "last_name": "Otieno",
            },
            {
                "email": "carol@example.com",
                "username": "carol_n",
                "first_name": "Carol",
                "last_name": "Njeri",
            },
            {
                "email": "dan@example.com",
                "username": "dan_k",
                "first_name": "Dan",
                "last_name": "Kipchoge",
            },
        ]
        members = {}
        created_count = 0

        for data in member_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "username": data["username"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "role": User.Role.MEMBER,
                },
            )

            if created:
                user.set_password(PASSWORD)
                user.save(update_fields=["password"])
                created_count += 1

            members[data["first_name"].lower()] = user

        return members, created_count

    def _create_categories(self):
        category_data = [
            (
                "Technology",
                "Events about software, startups, data, and digital tools.",
            ),
            (
                "Business",
                "Conferences and workshops for founders and professionals.",
            ),
            (
                "Health & Wellness",
                (
                    "Events focused on wellbeing, mindfulness, and healthy "
                    "living."
                ),
            ),
            (
                "Arts & Culture",
                "Creative events celebrating artists, culture, and design.",
            ),
            (
                "Education",
                "Learning programs, bootcamps, and skill-building events.",
            ),
            (
                "Networking",
                "Meetups designed for professional and community connections.",
            ),
        ]
        categories = {}
        created_count = 0

        for name, description in category_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )
            categories[name] = category
            created_count += int(created)

        return categories, created_count

    def _create_events(self, organisers, categories, now):
        event_data = self._event_data(organisers, categories, now)
        supports_remote = self._event_supports_remote()
        events = {}
        created_count = 0

        for data in event_data:
            title = data.pop("title")

            if not supports_remote:
                data.pop("is_remote", None)

            event, created = Event.objects.get_or_create(
                title=title,
                defaults=data,
            )
            events[title] = event
            created_count += int(created)

        return events, created_count

    def _event_data(self, organisers, categories, now):
        tech_start = now + timedelta(days=14)
        business_start = now + timedelta(days=21)
        wellness_start = now + timedelta(days=5)
        art_start = now - timedelta(days=30)
        django_start = now + timedelta(days=7)
        networking_start = now + timedelta(days=10)
        data_start = now + timedelta(days=3)
        ai_start = now + timedelta(days=45)

        return [
            {
                "title": "Nairobi Tech Summit 2025",
                "description": (
                    "A focused gathering for engineering leaders, startup "
                    "builders, and product teams shaping Kenya's digital "
                    "economy."
                ),
                "category": categories["Technology"],
                "organizer": organisers["events_ke"],
                "location": "KICC Nairobi",
                "start_datetime": tech_start,
                "end_datetime": tech_start + timedelta(hours=8),
                "capacity": 3,
                "status": Event.Status.PUBLISHED,
            },
            {
                "title": "Women in Business Nairobi",
                "description": (
                    "A practical leadership forum for women founders, finance "
                    "leaders, and operators growing resilient businesses."
                ),
                "category": categories["Business"],
                "organizer": organisers["events_ke"],
                "location": "Sarova Stanley Hotel",
                "start_datetime": business_start,
                "end_datetime": business_start + timedelta(hours=6),
                "capacity": 50,
                "status": Event.Status.PUBLISHED,
            },
            {
                "title": "Mindfulness & Wellness Workshop",
                "description": (
                    "A guided afternoon of mindfulness practice, stress "
                    "management, breathwork, and everyday wellness planning."
                ),
                "category": categories["Health & Wellness"],
                "organizer": organisers["events_ke"],
                "location": "The Hub Karen",
                "start_datetime": wellness_start,
                "end_datetime": wellness_start + timedelta(hours=3),
                "capacity": 20,
                "status": Event.Status.PUBLISHED,
            },
            {
                "title": "Digital Art Exhibition",
                "description": (
                    "A completed showcase of Nairobi digital artists "
                    "exploring identity, motion design, and interactive "
                    "installations."
                ),
                "category": categories["Arts & Culture"],
                "organizer": organisers["events_ke"],
                "location": "GoDown Arts Centre Nairobi",
                "start_datetime": art_start,
                "end_datetime": art_start + timedelta(hours=5),
                "capacity": 100,
                "status": Event.Status.COMPLETED,
            },
            {
                "title": "Python & Django Workshop",
                "description": (
                    "A hands-on workshop covering Django models, REST APIs, "
                    "authentication, testing, and deployment fundamentals."
                ),
                "category": categories["Technology"],
                "organizer": organisers["techtalks"],
                "location": "iHub Nairobi",
                "start_datetime": django_start,
                "end_datetime": django_start + timedelta(hours=4),
                "capacity": 30,
                "status": Event.Status.PUBLISHED,
            },
            {
                "title": "Startup Networking Night",
                "description": (
                    "An evening mixer for founders, builders, operators, and "
                    "investors looking for useful business connections."
                ),
                "category": categories["Networking"],
                "organizer": organisers["techtalks"],
                "location": "The Alchemist Nairobi",
                "start_datetime": networking_start,
                "end_datetime": networking_start + timedelta(hours=3),
                "capacity": 60,
                "status": Event.Status.PUBLISHED,
            },
            {
                "title": "Data Science Bootcamp",
                "description": (
                    "A full-day bootcamp on Python notebooks, data cleaning, "
                    "visualisation, SQL analysis, and model evaluation."
                ),
                "category": categories["Education"],
                "organizer": organisers["techtalks"],
                "location": "Strathmore University Nairobi",
                "start_datetime": data_start,
                "end_datetime": data_start + timedelta(hours=7),
                "capacity": 25,
                "status": Event.Status.PUBLISHED,
            },
            {
                "title": "Future of AI in Africa",
                "description": (
                    "A remote panel on AI products, policy, local datasets, "
                    "and responsible adoption across African markets."
                ),
                "category": categories["Technology"],
                "organizer": organisers["techtalks"],
                "location": "Online (Zoom)",
                "start_datetime": ai_start,
                "end_datetime": ai_start + timedelta(hours=2),
                "capacity": 200,
                "is_remote": True,
                "status": Event.Status.DRAFT,
            },
        ]

    def _event_supports_remote(self):
        return any(field.name == "is_remote" for field in Event._meta.fields)

    def _create_registrations(self, members, events, now):
        registration_data = [
            (
                members["alice"],
                events["Nairobi Tech Summit 2025"],
                Registration.Status.CONFIRMED,
                None,
            ),
            (
                members["bob"],
                events["Nairobi Tech Summit 2025"],
                Registration.Status.CONFIRMED,
                None,
            ),
            (
                members["carol"],
                events["Nairobi Tech Summit 2025"],
                Registration.Status.CONFIRMED,
                None,
            ),
            (
                members["dan"],
                events["Nairobi Tech Summit 2025"],
                Registration.Status.WAITLISTED,
                None,
            ),
            (
                members["alice"],
                events["Python & Django Workshop"],
                Registration.Status.CONFIRMED,
                None,
            ),
            (
                members["carol"],
                events["Python & Django Workshop"],
                Registration.Status.CONFIRMED,
                None,
            ),
            (
                members["bob"],
                events["Startup Networking Night"],
                Registration.Status.CONFIRMED,
                None,
            ),
            (
                members["dan"],
                events["Startup Networking Night"],
                Registration.Status.CONFIRMED,
                None,
            ),
            (
                members["alice"],
                events["Data Science Bootcamp"],
                Registration.Status.CONFIRMED,
                None,
            ),
            (
                members["carol"],
                events["Mindfulness & Wellness Workshop"],
                Registration.Status.CONFIRMED,
                None,
            ),
            (
                members["bob"],
                events["Mindfulness & Wellness Workshop"],
                Registration.Status.CONFIRMED,
                None,
            ),
            (
                members["alice"],
                events["Women in Business Nairobi"],
                Registration.Status.CONFIRMED,
                None,
            ),
            (
                members["alice"],
                events["Digital Art Exhibition"],
                Registration.Status.CANCELLED,
                now - timedelta(days=25),
            ),
        ]
        registrations = []

        for user, event, status, cancelled_at in registration_data:
            registration, _ = Registration.objects.get_or_create(
                event=event,
                user=user,
                defaults={
                    "status": status,
                    "ticket_number": generate_ticket_number(),
                    "cancelled_at": cancelled_at,
                },
            )
            registrations.append(registration)

        return registrations

    def _print_summary(
        self,
        organiser_count,
        member_count,
        category_count,
        event_count,
        registrations,
    ):
        confirmed_count = sum(
            item.status == Registration.Status.CONFIRMED
            for item in registrations
        )
        waitlisted_count = sum(
            item.status == Registration.Status.WAITLISTED
            for item in registrations
        )
        cancelled_count = sum(
            item.status == Registration.Status.CANCELLED
            for item in registrations
        )
        total_count = len(registrations)

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {organiser_count} organisers, "
                f"{member_count} members"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f"✓ Created {category_count} categories")
        )
        self.stdout.write(
            self.style.SUCCESS(f"✓ Created {event_count} events")
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {total_count} registrations "
                f"({confirmed_count} confirmed, "
                f"{waitlisted_count} waitlisted, "
                f"{cancelled_count} cancelled)"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "✓ Nairobi Tech Summit 2025 is FULL — dan is waitlisted"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "✓ Seed complete — login: organizer1@example.com / "
                "TestPass123!"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "✓ Swagger: GET /api/events/ → 7 events listed"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "✓ Swagger: GET /api/events/?upcoming=true → "
                "6 upcoming events"
            )
        )


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each section of the command does and why
#
# The imports load Django's management command tools, timezone helpers, the
# active custom user model, event models, and generate_ticket_number.
#
# PASSWORD stores the shared demo password in one place so every seeded account
# uses the same known test credential.
#
# Command is the management command class. Django discovers it because the file
# is named events/management/commands/seed_demo_data.py.
#
# handle is the entry point. It configures UTF-8 output, skips when categories
# already exist, creates the demo data inside one database transaction, and
# prints the final summary.
#
# _configure_output lets the requested checkmark character print correctly in
# Windows terminals that support stream reconfiguration.
#
# _create_organisers creates the two organizer accounts.
#
# _create_members creates the four member accounts.
#
# _create_categories creates the six event categories.
#
# _create_events creates the eight demo events with realistic descriptions,
# timezone-aware start and end datetimes, capacities, and statuses.
#
# _event_data keeps the event definitions separate from the creation loop so
# the command is easier to read.
#
# _event_supports_remote checks whether the Event model has an is_remote field.
# This keeps the command compatible with projects that include that field and
# projects that do not.
#
# _create_registrations creates the requested confirmed, waitlisted, and
# cancelled registrations.
#
# _print_summary reports what the command created and gives useful Swagger
# checks for reviewers.
#
# Why capacity=3 on the Tech Summit is intentional
#
# Nairobi Tech Summit 2025 has capacity=3 on purpose. Alice, Bob, and Carol
# fill the three confirmed seats, so Dan must be waitlisted. This makes the
# waitlist feature visible immediately in demo data.
#
# Why generate_ticket_number() is called instead of hardcoding
#
# generate_ticket_number() uses the same ticket-generation logic as the real
# registration flow. Calling it prevents duplicate ticket numbers and avoids
# fake hardcoded values that might not match production behavior.
#
# Why one past COMPLETED event is included
#
# Digital Art Exhibition is a past completed event so the API can demonstrate
# the difference between all events and upcoming events. It also gives the demo
# data a cancelled registration to test cancellation display.
#
# Why idempotency matters and how get_or_create achieves it
#
# Idempotency matters because seed commands are often run more than once during
# setup, review, or deployment. Running twice should not create duplicate
# users, events, categories, or registrations.
#
# get_or_create first searches by stable fields such as email, category name,
# event title, or event plus user. If a row exists, Django returns it. If it
# does not exist, Django creates it with the defaults.
#
# The command also checks Category.objects.exists() at the start. If categories
# already exist, it prints "Already seeded. Skipping." and returns early.
#
# What to verify after running the command
#
# Run python manage.py seed_demo_data and confirm it finishes without errors.
#
# Run it a second time and confirm it prints Already seeded. Skipping.
#
# Check GET /api/events/?upcoming=true and confirm it returns 6 events, not the
# completed past event.
#
# Check GET /api/events/<nairobi_tech_summit_pk>/ and confirm spots_left is 0
# and is_full is true.
#
# Check Dan's Nairobi Tech Summit registration and confirm status is
# WAITLISTED.
#
# Cancel Alice's Nairobi Tech Summit registration through the cancel endpoint
# and confirm Dan is promoted from WAITLISTED to CONFIRMED.
#
# ============================================================
# END OF REVIEW
# ============================================================
