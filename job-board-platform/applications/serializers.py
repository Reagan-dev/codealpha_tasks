import os

from django.conf import settings
from rest_framework import serializers

from jobs.serializers import JobDetailSerializer

from .models import Application, ApplicationNote, Resume


class ResumeSerializer(serializers.ModelSerializer):
    """Serialize saved resume data."""

    class Meta:
        model = Resume
        fields = ("id", "title", "file", "uploaded_at", "is_primary")
        read_only_fields = ("uploaded_at",)


class ResumeUploadSerializer(serializers.ModelSerializer):
    """Validate resume upload requests."""

    class Meta:
        model = Resume
        fields = ("title", "file")

    def validate_file(self, value):
        extension = os.path.splitext(value.name)[1].lower()

        if extension not in (".pdf", ".docx"):
            raise serializers.ValidationError(
                "Resume file must be a PDF or DOCX file."
            )

        if value.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            raise serializers.ValidationError(
                "Resume file size must be 5 MB or less."
            )

        return value


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Validate job application creation requests."""

    class Meta:
        model = Application
        fields = ("job", "resume", "cover_letter")


class ApplicationListSerializer(serializers.ModelSerializer):
    """Serialize application summary data for candidate views."""

    job_title = serializers.CharField(source="job.title", read_only=True)
    company = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = (
            "id",
            "job_title",
            "company",
            "status",
            "applied_at",
        )

    def get_company(self, obj):
        profile = getattr(obj.job.employer, "employer_profile", None)

        if profile is None:
            return obj.job.employer.email

        return profile.company_name


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Serialize full application detail data."""

    resume_download_url = serializers.SerializerMethodField()
    job_detail = JobDetailSerializer(source="job", read_only=True)
    resume = ResumeSerializer(read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "job",
            "job_detail",
            "candidate",
            "resume",
            "resume_download_url",
            "cover_letter",
            "status",
            "applied_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_resume_download_url(self, obj):
        if obj.resume is None or not obj.resume.file:
            return None

        request = self.context.get("request")

        if request is None:
            return obj.resume.file.url

        return request.build_absolute_uri(obj.resume.file.url)


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """Validate allowed application status transitions."""

    allowed_transitions = {
        Application.Status.APPLIED: {
            Application.Status.REVIEWING,
            Application.Status.REJECTED,
        },
        Application.Status.REVIEWING: {
            Application.Status.INTERVIEW,
            Application.Status.REJECTED,
        },
        Application.Status.INTERVIEW: {
            Application.Status.OFFER,
            Application.Status.REJECTED,
        },
        Application.Status.OFFER: {
            Application.Status.REJECTED,
        },
        Application.Status.REJECTED: set(),
    }

    class Meta:
        model = Application
        fields = ("status",)

    def validate_status(self, value):
        application = self.instance

        if application is None:
            return value

        if value == application.status:
            return value

        allowed_statuses = self.allowed_transitions.get(
            application.status,
            set(),
        )

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                "Invalid application status transition."
            )

        return value


class ApplicationNoteSerializer(serializers.ModelSerializer):
    """Serialize private employer notes."""

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = ApplicationNote
        fields = ("note", "created_by_username", "created_at")
        read_only_fields = ("created_by_username", "created_at")


class EmployerApplicationSerializer(serializers.ModelSerializer):
    """Serialize application data for employer review."""

    candidate_name = serializers.SerializerMethodField()
    headline = serializers.CharField(
        source="candidate.candidate_profile.headline",
        read_only=True,
    )
    skills = serializers.SerializerMethodField()
    resume = ResumeSerializer(read_only=True)
    notes = ApplicationNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "candidate_name",
            "headline",
            "skills",
            "status",
            "resume",
            "cover_letter",
            "applied_at",
            "notes",
        )

    def get_candidate_name(self, obj):
        full_name = obj.candidate.get_full_name()

        if full_name:
            return full_name

        return obj.candidate.email

    def get_skills(self, obj):
        profile = getattr(obj.candidate, "candidate_profile", None)

        if profile is None or not profile.skills:
            return []

        return [
            skill.strip()
            for skill in profile.skills.split(",")
            if skill.strip()
        ]


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# ResumeSerializer returns saved resume data for read endpoints.
#
# ResumeUploadSerializer accepts title and file for upload endpoints.
#
# validate_file checks that uploaded resumes are PDF or DOCX files and no
# larger than the 5 MB upload limit from settings.
#
# ApplicationCreateSerializer accepts job, optional resume, and cover letter
# when a candidate applies.
#
# ApplicationListSerializer returns a compact candidate-facing application
# summary with job title, company, status, and applied date.
#
# get_company returns the employer company name and falls back to email if the
# employer has no profile.
#
# ApplicationDetailSerializer returns all application fields, nested job
# details, nested resume data, and a resume download URL.
#
# get_resume_download_url returns an absolute URL when request context exists
# and a relative media URL otherwise.
#
# ApplicationStatusUpdateSerializer validates status-only updates.
#
# validate_status enforces allowed application workflow transitions.
#
# ApplicationNoteSerializer returns private note text, author username, and
# creation time.
#
# EmployerApplicationSerializer returns the employer review view with candidate
# name, headline, skills, status, resume, cover letter, applied date, and
# notes.
#
# get_candidate_name prefers the candidate's full name and falls back to email.
#
# get_skills returns candidate skills as a clean list.
#
# Important decisions that were made and why
#
# Resume upload validation checks extension and size in the serializer because
# those are request-level validation rules.
#
# Application detail uses JobDetailSerializer so job information is consistent
# with the jobs API.
#
# Status transitions are enforced in the serializer so invalid PATCH requests
# return clear 400 errors.
#
# EmployerApplicationSerializer does not expose every user field because
# employers need application review information, not full account data.
#
# What you should read and understand before you review the code
#
# Read DRF ModelSerializer and nested serializers.
#
# Read file upload validation with serializer field validators.
#
# Read SerializerMethodField for computed response fields.
#
# Read status transition validation using self.instance.
#
# ============================================================
# END OF REVIEW
# ============================================================
