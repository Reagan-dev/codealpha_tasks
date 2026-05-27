from django.utils import timezone
from rest_framework import serializers

from accounts.serializers import EmployerProfileSerializer

from .models import JobCategory, JobListing


class JobCategorySerializer(serializers.ModelSerializer):
    """Serialize job category data."""

    class Meta:
        model = JobCategory
        fields = ("id", "name", "description")


class JobListSerializer(serializers.ModelSerializer):
    """Serialize compact job listing data for list pages."""

    company_name = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = JobListing
        fields = (
            "id",
            "title",
            "company_name",
            "location",
            "is_remote",
            "job_type",
            "experience_level",
            "salary_min",
            "salary_max",
            "is_featured",
            "status",
            "view_count",
            "application_deadline",
            "created_at",
            "is_expired",
        )

    def get_company_name(self, obj):
        profile = getattr(obj.employer, "employer_profile", None)

        if profile is None:
            return obj.employer.email

        return profile.company_name


class JobDetailSerializer(JobListSerializer):
    """Serialize full job listing data for detail pages."""

    category = JobCategorySerializer(read_only=True)
    employer_profile = serializers.SerializerMethodField()

    class Meta(JobListSerializer.Meta):
        fields = JobListSerializer.Meta.fields + (
            "description",
            "requirements",
            "category",
            "employer_profile",
        )

    def get_employer_profile(self, obj):
        profile = getattr(obj.employer, "employer_profile", None)

        if profile is None:
            return None

        return EmployerProfileSerializer(
            profile,
            context=self.context,
        ).data


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """Validate job listing create and update requests."""

    class Meta:
        model = JobListing
        fields = (
            "title",
            "category",
            "description",
            "requirements",
            "location",
            "is_remote",
            "job_type",
            "experience_level",
            "salary_min",
            "salary_max",
            "is_featured",
            "status",
            "application_deadline",
        )

    def validate(self, attrs):
        salary_min = attrs.get(
            "salary_min",
            getattr(self.instance, "salary_min", None),
        )
        salary_max = attrs.get(
            "salary_max",
            getattr(self.instance, "salary_max", None),
        )

        if (
            salary_min is not None
            and salary_max is not None
            and salary_min > salary_max
        ):
            raise serializers.ValidationError(
                {"salary_max": "Salary max must be greater than salary min."}
            )

        return attrs

    def validate_application_deadline(self, value):
        if value is not None and value <= timezone.localdate():
            raise serializers.ValidationError(
                "Application deadline must be in the future."
            )

        return value


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# JobCategorySerializer converts job categories to and from API data.
#
# JobListSerializer returns a compact job listing response for list pages.
#
# company_name is a computed field because the company name lives on the
# employer profile, not directly on JobListing.
#
# get_company_name returns the employer company name and falls back to email if
# the employer profile does not exist.
#
# JobDetailSerializer extends JobListSerializer and adds description,
# requirements, category details, and employer profile details.
#
# get_employer_profile returns nested employer profile data when it exists.
#
# JobCreateUpdateSerializer validates writable job listing fields.
#
# validate checks salary_min and salary_max together because the rule depends
# on both fields.
#
# validate_application_deadline rejects today or past dates so new listings
# cannot be created with expired deadlines.
#
# Important decisions that were made and why
#
# Separate list, detail, and write serializers keep response payloads focused.
#
# EmployerProfileSerializer is reused for employer details instead of
# duplicating profile fields in the jobs app.
#
# validate uses existing instance values during PATCH so partial updates still
# enforce salary range rules.
#
# What you should read and understand before you review the code
#
# Read DRF ModelSerializer basics.
#
# Read SerializerMethodField for related-object display values.
#
# Read serializer-level validate and field-level validation methods.
#
# Read why list and detail serializers are often separated.
#
# ============================================================
# END OF REVIEW
# ============================================================
