from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import CandidateProfile, EmployerProfile


User = get_user_model()


class PasswordMatchMixin:
    """Validate matching password and password2 fields."""

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."}
            )

        return attrs


class EmployerRegistrationSerializer(
    PasswordMatchMixin,
    serializers.ModelSerializer,
):
    """Register an employer user and create an employer profile."""

    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    company_name = serializers.CharField(write_only=True)
    industry = serializers.CharField(write_only=True)
    location = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password2",
            "first_name",
            "last_name",
            "company_name",
            "industry",
            "location",
        )

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        company_name = validated_data.pop("company_name")
        industry = validated_data.pop("industry")
        location = validated_data.pop("location")

        with transaction.atomic():
            user = User.objects.create_user(
                password=password,
                role=User.Role.EMPLOYER,
                **validated_data,
            )
            EmployerProfile.objects.create(
                user=user,
                company_name=company_name,
                company_description="",
                industry=industry,
                company_size=EmployerProfile.CompanySize.STARTUP,
                location=location,
            )

        return user


class CandidateRegistrationSerializer(
    PasswordMatchMixin,
    serializers.ModelSerializer,
):
    """Register a candidate user and create a candidate profile."""

    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password2",
            "first_name",
            "last_name",
        )

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        with transaction.atomic():
            user = User.objects.create_user(
                password=password,
                role=User.Role.CANDIDATE,
                **validated_data,
            )
            CandidateProfile.objects.create(
                user=user,
                headline="",
                skills="",
            )

        return user


class EmployerProfileSerializer(serializers.ModelSerializer):
    """Serialize employer company profile data."""

    class Meta:
        model = EmployerProfile
        fields = (
            "id",
            "user",
            "company_name",
            "company_description",
            "website",
            "industry",
            "company_size",
            "location",
            "logo",
            "verified",
        )
        read_only_fields = ("user", "verified")


class CandidateProfileSerializer(serializers.ModelSerializer):
    """Serialize candidate profile data with skills as a list on read."""

    skills = serializers.SerializerMethodField()

    class Meta:
        model = CandidateProfile
        fields = (
            "id",
            "user",
            "headline",
            "skills",
            "experience_years",
            "education",
            "linkedin_url",
            "portfolio_url",
        )
        read_only_fields = ("user",)

    def get_skills(self, obj):
        if not obj.skills:
            return []

        return [
            skill.strip()
            for skill in obj.skills.split(",")
            if skill.strip()
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """Serialize user data with the matching role profile nested inside."""

    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "bio",
            "profile_picture",
            "profile",
        )

    def get_profile(self, obj):
        if obj.role == User.Role.EMPLOYER:
            profile = getattr(obj, "employer_profile", None)

            if profile is None:
                return None

            return EmployerProfileSerializer(
                profile,
                context=self.context,
            ).data

        profile = getattr(obj, "candidate_profile", None)

        if profile is None:
            return None

        return CandidateProfileSerializer(
            profile,
            context=self.context,
        ).data


