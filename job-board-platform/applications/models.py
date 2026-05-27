from django.conf import settings
from django.db import models

from jobs.models import JobListing


class Resume(models.Model):
    """Resume file uploaded by a candidate."""

    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes",
        help_text="Candidate user who uploaded this resume.",
    )
    title = models.CharField(
        max_length=150,
        help_text="Resume title, such as My Software Dev Resume.",
    )
    file = models.FileField(
        upload_to="resumes/",
        help_text="Uploaded resume file.",
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time this resume was uploaded.",
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Shows whether this is the candidate's main resume.",
    )

    class Meta:
        verbose_name = "resume"
        verbose_name_plural = "resumes"
        ordering = ["-uploaded_at", "title"]

    def __str__(self):
        return f"{self.title} - {self.candidate}"


class Application(models.Model):
    """Candidate application submitted for a job listing."""

    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        REVIEWING = "REVIEWING", "Reviewing"
        INTERVIEW = "INTERVIEW", "Interview"
        OFFER = "OFFER", "Offer"
        REJECTED = "REJECTED", "Rejected"

    job = models.ForeignKey(
        JobListing,
        on_delete=models.CASCADE,
        related_name="applications",
        help_text="Job listing this application belongs to.",
    )
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
        help_text="Candidate user who submitted this application.",
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
        help_text="Optional resume attached to this application.",
    )
    cover_letter = models.TextField(
        null=True,
        blank=True,
        help_text="Optional cover letter written by the candidate.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPLIED,
        help_text="Current review status of this application.",
    )
    applied_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time this application was submitted.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time this application was last updated.",
    )

    class Meta:
        verbose_name = "application"
        verbose_name_plural = "applications"
        ordering = ["-applied_at"]
        unique_together = ["job", "candidate"]

    def __str__(self):
        return f"{self.candidate} applied to {self.job}"


class ApplicationNote(models.Model):
    """Private employer note for a job application."""

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="notes",
        help_text="Application this private note belongs to.",
    )
    note = models.TextField(
        help_text="Private note visible to employers or staff.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="application_notes",
        help_text="Employer or staff user who created this note.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time this note was created.",
    )

    class Meta:
        verbose_name = "application note"
        verbose_name_plural = "application notes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note for {self.application}"


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# Resume stores resume files uploaded by candidates.
#
# candidate uses settings.AUTH_USER_MODEL so the applications app works with
# the custom accounts.User model.
#
# file uploads resumes into the resumes/ media folder.
#
# is_primary marks the candidate's main resume.
#
# Application stores one candidate's application for one job listing.
#
# Status is a TextChoices class that tracks the application workflow:
# APPLIED, REVIEWING, INTERVIEW, OFFER, or REJECTED.
#
# job connects the application to the job listing being applied for.
#
# candidate connects the application to the user who submitted it.
#
# resume is optional and uses SET_NULL so the application can remain even if a
# resume file record is removed.
#
# cover_letter is optional because some applications may not require one.
#
# applied_at and updated_at provide audit timestamps.
#
# ApplicationNote stores private employer notes about an application.
#
# created_by uses PROTECT so notes keep their author reference and employer
# review history is not silently broken.
#
# __str__ methods return readable application and note labels for admin pages
# and debugging.
#
# Important decisions that were made and why
#
# Application has unique_together on job and candidate so a candidate cannot
# apply to the same job more than once.
#
# Application.job uses CASCADE because applications are only meaningful while
# their job listing exists.
#
# Resume.candidate and Application.candidate use CASCADE because deleting a
# candidate account should remove that candidate's resumes and applications.
#
# ApplicationNote.application uses CASCADE because notes are only meaningful
# while their application exists.
#
# What you should read and understand before you review the code
#
# Read Django FileField and media upload settings.
#
# Read ForeignKey on_delete behaviors: CASCADE, SET_NULL, and PROTECT.
#
# Read unique_together and how it prevents duplicate applications.
#
# Read TextChoices for workflow status fields.
#
# ============================================================
# END OF REVIEW
# ============================================================
