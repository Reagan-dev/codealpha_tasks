import logging

from django.conf import settings
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


def send_welcome_email(user):
    """Send a welcome email after a user registers."""
    subject = "Welcome to Event Registration System"
    message = (
        f"Dear {user.first_name}, welcome to the Event Registration System. "
        "Your account has been created successfully."
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
            "Failed to send welcome email to %s.",
            user.email,
        )


