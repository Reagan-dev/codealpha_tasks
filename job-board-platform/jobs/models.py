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


