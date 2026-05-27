from django.conf import settings
from django.db import models
from django.utils import timezone


class JobCategory(models.Model):
    """Category used to group similar job listings."""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique job category name.",
    )
    description = models.TextField(
        help_text="Short description of jobs in this category.",
    )

    class Meta:
        verbose_name = "job category"
        verbose_name_plural = "job categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class JobListing(models.Model):
    """Job post created by an employer."""

    class JobType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full time"
        PART_TIME = "PART_TIME", "Part time"
        CONTRACT = "CONTRACT", "Contract"
        INTERNSHIP = "INTERNSHIP", "Internship"
        FREELANCE = "FREELANCE", "Freelance"

    class ExperienceLevel(models.TextChoices):
        ENTRY = "ENTRY", "Entry"
        MID = "MID", "Mid"
        SENIOR = "SENIOR", "Senior"
        LEAD = "LEAD", "Lead"
        EXECUTIVE = "EXECUTIVE", "Executive"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        CLOSED = "CLOSED", "Closed"

    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="job_listings",
        help_text="Employer user who posted this job.",
    )
    title = models.CharField(
        max_length=150,
        help_text="Public job title shown to candidates.",
    )
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.PROTECT,
        related_name="job_listings",
        help_text="Category this job belongs to.",
    )
    description = models.TextField(
        help_text="Detailed job description.",
    )
    requirements = models.TextField(
        help_text="Skills, qualifications, and responsibilities required.",
    )
    location = models.CharField(
        max_length=150,
        help_text="Job location or headquarters.",
    )
    is_remote = models.BooleanField(
        default=False,
        help_text="Shows whether this job can be done remotely.",
    )
    job_type = models.CharField(
        max_length=20,
        choices=JobType.choices,
        help_text="Employment type for this job.",
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        help_text="Experience level expected for this role.",
    )
    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Optional minimum salary for this job.",
    )
    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Optional maximum salary for this job.",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Shows whether this job should be highlighted.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text="Publication status of this job listing.",
    )
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times candidates have viewed this listing.",
    )
    application_deadline = models.DateField(
        null=True,
        blank=True,
        help_text="Optional final date candidates can apply.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time this job was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time this job was last updated.",
    )

    class Meta:
        verbose_name = "job listing"
        verbose_name_plural = "job listings"
        ordering = ["-created_at", "title"]

    @property
    def is_expired(self):
        """Return True when the deadline exists and has passed."""
        return (
            self.application_deadline is not None
            and self.application_deadline < timezone.localdate()
        )

    def __str__(self):
        return f"{self.title} - {self.employer}"


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# JobCategory groups job listings into sections such as Software Development,
# Design, Marketing, or Finance.
#
# name is unique so duplicate categories are not created by accident.
#
# JobListing stores one public job post created by an employer.
#
# JobType is a TextChoices class that limits job_type to FULL_TIME, PART_TIME,
# CONTRACT, INTERNSHIP, or FREELANCE.
#
# ExperienceLevel is a TextChoices class that limits experience_level to
# ENTRY, MID, SENIOR, LEAD, or EXECUTIVE.
#
# Status is a TextChoices class that tracks whether a job is DRAFT, ACTIVE, or
# CLOSED.
#
# employer uses settings.AUTH_USER_MODEL so the jobs app works with the custom
# accounts.User model without importing it directly.
#
# employer uses PROTECT so job history is not deleted accidentally when an
# employer account is removed.
#
# category also uses PROTECT so categories with job listings cannot be deleted
# by accident.
#
# salary_min and salary_max are optional because many job posts do not publish
# salary ranges.
#
# view_count tracks listing popularity.
#
# application_deadline is optional because some jobs stay open until filled.
#
# created_at and updated_at are timestamps for sorting and auditing.
#
# is_expired returns True only when the job has a deadline and that deadline is
# before today's local date.
#
# __str__ returns the title and employer so job listings are easy to recognize.
#
# Important decisions that were made and why
#
# DecimalField is used for salary values because money should not be stored as
# floating point numbers.
#
# is_expired is a property instead of a database field because it is calculated
# from application_deadline and today's date.
#
# timezone.localdate is used so expiry checks follow Django's configured
# timezone.
#
# What you should read and understand before you review the code
#
# Read Django ForeignKey and on_delete=PROTECT.
#
# Read Django model properties with @property.
#
# Read DateField comparisons and timezone.localdate.
#
# Read DecimalField and why it is used for money.
#
# ============================================================
# END OF REVIEW
# ============================================================
