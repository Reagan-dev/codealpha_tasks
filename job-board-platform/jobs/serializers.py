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


