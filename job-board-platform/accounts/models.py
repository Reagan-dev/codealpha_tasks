from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for employers and candidates."""

    class Role(models.TextChoices):
        EMPLOYER = "EMPLOYER", "Employer"
        CANDIDATE = "CANDIDATE", "Candidate"

    email = models.EmailField(
        unique=True,
        help_text="Unique email address used to sign in.",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CANDIDATE,
        help_text="User role inside the job board platform.",
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Optional contact phone number.",
    )
    bio = models.TextField(
        null=True,
        blank=True,
        help_text="Short user biography shown on the profile.",
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True,
        help_text="Optional profile picture for the user.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["email"]

    def __str__(self):
        return self.email


class EmployerProfile(models.Model):
    """Company profile owned by an employer user."""

    class CompanySize(models.TextChoices):
        STARTUP = "STARTUP", "Startup"
        SMALL = "SMALL", "Small"
        MEDIUM = "MEDIUM", "Medium"
        LARGE = "LARGE", "Large"
        ENTERPRISE = "ENTERPRISE", "Enterprise"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employer_profile",
        help_text="Employer user who owns this company profile.",
    )
    company_name = models.CharField(
        max_length=150,
        unique=True,
        help_text="Unique company name shown on job listings.",
    )
    company_description = models.TextField(
        help_text="Overview of the company and what it does.",
    )
    website = models.URLField(
        null=True,
        blank=True,
        help_text="Optional company website URL.",
    )
    industry = models.CharField(
        max_length=100,
        help_text="Primary industry where the company operates.",
    )
    company_size = models.CharField(
        max_length=20,
        choices=CompanySize.choices,
        help_text="Approximate size of the company.",
    )
    location = models.CharField(
        max_length=150,
        help_text="Main company location.",
    )
    logo = models.ImageField(
        upload_to="company_logos/",
        null=True,
        blank=True,
        help_text="Optional company logo image.",
    )
    verified = models.BooleanField(
        default=False,
        help_text="Shows whether admins have verified this employer.",
    )

    class Meta:
        verbose_name = "employer profile"
        verbose_name_plural = "employer profiles"
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name


class CandidateProfile(models.Model):
    """Professional profile owned by a candidate user."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="candidate_profile",
        help_text="Candidate user who owns this professional profile.",
    )
    headline = models.CharField(
        max_length=150,
        help_text="Short professional headline, such as Senior Django Dev.",
    )
    skills = models.TextField(
        help_text="Comma-separated list of candidate skills.",
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        help_text="Total years of professional experience.",
    )
    education = models.TextField(
        null=True,
        blank=True,
        help_text="Optional education summary.",
    )
    linkedin_url = models.URLField(
        null=True,
        blank=True,
        help_text="Optional LinkedIn profile URL.",
    )
    portfolio_url = models.URLField(
        null=True,
        blank=True,
        help_text="Optional portfolio or personal website URL.",
    )

    class Meta:
        verbose_name = "candidate profile"
        verbose_name_plural = "candidate profiles"
        ordering = ["user__email"]

    def __str__(self):
        return f"{self.user.email} - {self.headline}"


