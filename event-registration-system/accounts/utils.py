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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# send_welcome_email sends a welcome message after a new user registers. It
# keeps email-sending code outside serializers or views so account code stays
# easier to read and test.
#
# The function uses Django's send_mail helper because it works with the email
# backend configured in settings. In development, the message prints to the
# console. In production, it can go through SMTP.
#
# The function catches exceptions and logs them. A welcome email is useful, but
# a mail server problem should not stop a user account from being created.
#
# Important decisions that were made and why
#
# settings.EMAIL_HOST_USER is used as the sender so the email address is
# configured in one place.
#
# logger.exception is used because it records the error message and traceback,
# which helps with debugging failed emails.
#
# What you should read and understand before you review the code
#
# Read Django's send_mail documentation.
#
# Read Django email backend settings so you understand why console email is used
# during development and SMTP is used in production.
#
# Read Python logging basics, especially logger.exception.
#
# ============================================================
# END OF REVIEW
# ============================================================
