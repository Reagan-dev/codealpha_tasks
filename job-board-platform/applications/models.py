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


