import logging
import random
import string
from datetime import date

from django.conf import settings
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


def generate_ticket_number():
    """Return a unique ticket number for an event registration."""
    from .models import Registration

    today = date.today().strftime("%Y%m%d")
    characters = string.ascii_uppercase + string.digits

    while True:
        random_part = "".join(random.choices(characters, k=6))
        ticket_number = f"TKT-{today}-{random_part}"

        if not Registration.objects.filter(
            ticket_number=ticket_number,
        ).exists():
            return ticket_number


def send_registration_email(user, registration, event):
    """Send a registration confirmation email to the user."""
    subject = f"Registration Confirmed — {event.title}"
    message = (
        f"Dear {user.first_name}, your registration for {event.title} on "
        f"{event.start_datetime} is confirmed. Your ticket number is "
        f"{registration.ticket_number}."
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send registration email to %s for event %s.",
            user.email,
            event.pk,
        )


def send_cancellation_email(user, event):
    """Send a registration cancellation confirmation email to the user."""
    subject = f"Registration Cancelled — {event.title}"
    message = (
        f"Dear {user.first_name}, your registration for {event.title} on "
        f"{event.start_datetime} has been cancelled."
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send cancellation email to %s for event %s.",
            user.email,
            event.pk,
        )



