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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# generate_ticket_number creates ticket numbers in the format
# TKT-YYYYMMDD-XXXXXX. The date makes the ticket readable, and the random
# uppercase letters and numbers make it hard to guess.
#
# generate_ticket_number checks the Registration table before returning. This
# protects the unique ticket_number database field from collisions. A collision
# is unlikely, but checking keeps the function safe.
#
# send_registration_email sends a confirmation email after a successful event
# registration. It includes the event title, start date and time, and ticket
# number so the user has the important details.
#
# send_cancellation_email sends an email after a registration is cancelled. It
# confirms the cancellation without needing the full Registration object.
#
# Each email function catches exceptions and logs them. Email should not crash
# the whole registration or cancellation flow if the mail server is unavailable.
#
# Important decisions that were made and why
#
# The Registration import is inside generate_ticket_number to avoid loading the
# model too early when Django imports utility modules.
#
# settings.EMAIL_HOST_USER is used as from_email so the sender stays controlled
# by settings and can change between development and production.
#
# logger.exception is used inside except blocks because it records both the
# custom message and the original traceback.
#
# What you should read and understand before you review the code
#
# Read Django's send_mail documentation so you understand subject, message,
# from_email, recipient_list, and fail_silently.
#
# Read Python logging basics, especially logger.exception.
#
# Read Django model uniqueness and why code checks plus database constraints are
# useful together.
#
# ============================================================
# END OF REVIEW
# ============================================================
