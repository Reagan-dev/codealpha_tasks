import logging

from django.conf import settings
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


def send_application_confirmation_email(candidate, application, job):
    """Send a confirmation email after a candidate applies to a job."""
    subject = f"Application received for {job.title}"
    message = (
        f"Hello {candidate.first_name or candidate.email},\n\n"
        f"Your application for {job.title} has been received.\n"
        f"Application status: {application.status}.\n\n"
        "Thank you for using the Job Board Platform."
    )

    return _send_email(
        subject=subject,
        message=message,
        recipient_list=[candidate.email],
    )


def send_status_update_email(candidate, application, job):
    """Send an email when an application status changes."""
    subject = f"Application status updated for {job.title}"
    message = (
        f"Hello {candidate.first_name or candidate.email},\n\n"
        f"Your application for {job.title} is now {application.status}.\n\n"
        "Please sign in to your account for more details."
    )

    return _send_email(
        subject=subject,
        message=message,
        recipient_list=[candidate.email],
    )


def send_new_application_notification(employer, application, job):
    """Send an email to an employer when a new application is submitted."""
    candidate = application.candidate
    candidate_name = candidate.get_full_name() or candidate.email
    subject = f"New application for {job.title}"
    message = (
        f"Hello {employer.first_name or employer.email},\n\n"
        f"{candidate_name} has applied for {job.title}.\n"
        "Please sign in to review the application."
    )

    return _send_email(
        subject=subject,
        message=message,
        recipient_list=[employer.email],
    )


def _send_email(subject, message, recipient_list):
    """Send one email and return True when sending succeeds."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send email '%s' to %s.",
            subject,
            ", ".join(recipient_list),
        )
        return False

    return True


