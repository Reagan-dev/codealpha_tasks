from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import (
    IsApplicationOwner,
    IsCandidate,
    IsEmployer,
    IsJobOwner,
)
from jobs.models import JobListing

from .models import Application, Resume
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationDetailSerializer,
    ApplicationListSerializer,
    ApplicationStatusUpdateSerializer,
    EmployerApplicationSerializer,
    ResumeSerializer,
    ResumeUploadSerializer,
)
from .utils import (
    send_application_confirmation_email,
    send_new_application_notification,
    send_status_update_email,
)


class ResumeUploadView(CreateAPIView):
    """Upload a resume for the authenticated candidate."""

    serializer_class = ResumeUploadSerializer
    permission_classes = [IsCandidate]

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user)


class ResumeListView(ListAPIView):
    """List resumes uploaded by the authenticated candidate."""

    serializer_class = ResumeSerializer
    permission_classes = [IsCandidate]

    def get_queryset(self):
        return Resume.objects.filter(candidate=self.request.user)


class ResumeDeleteView(DestroyAPIView):
    """Delete a resume owned by the authenticated candidate."""

    serializer_class = ResumeSerializer
    permission_classes = [IsCandidate, IsApplicationOwner]

    def get_queryset(self):
        return Resume.objects.filter(candidate=self.request.user)


class ApplicationCreateView(CreateAPIView):
    """Create a job application for the authenticated candidate."""

    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsCandidate]

    def perform_create(self, serializer):
        candidate = self.request.user
        job = serializer.validated_data["job"]
        resume = serializer.validated_data.get("resume")

        self._validate_resume_owner(resume, candidate)
        self._validate_job_can_receive_application(job)
        self._validate_not_already_applied(job, candidate)

        application = serializer.save(candidate=candidate)
        send_application_confirmation_email(candidate, application, job)
        send_new_application_notification(job.employer, application, job)

    def _validate_resume_owner(self, resume, candidate):
        if resume is not None and resume.candidate != candidate:
            raise ValidationError(
                {"resume": "You can only use your own resume."}
            )

    def _validate_job_can_receive_application(self, job):
        if job.status != JobListing.Status.ACTIVE or job.is_expired:
            raise ValidationError(
                {"job": "This job is not accepting applications."}
            )

    def _validate_not_already_applied(self, job, candidate):
        already_applied = Application.objects.filter(
            job=job,
            candidate=candidate,
        ).exists()

        if already_applied:
            raise ValidationError(
                {"job": "You have already applied to this job."}
            )


class CandidateApplicationListView(ListAPIView):
    """List applications submitted by the authenticated candidate."""

    serializer_class = ApplicationListSerializer
    permission_classes = [IsCandidate]

    def get_queryset(self):
        return (
            Application.objects.select_related(
                "job",
                "job__employer",
                "job__employer__employer_profile",
            )
            .filter(candidate=self.request.user)
        )


class EmployerApplicationListView(ListAPIView):
    """List applications for jobs owned by the authenticated employer."""

    serializer_class = EmployerApplicationSerializer
    permission_classes = [IsEmployer]

    def get_queryset(self):
        queryset = (
            Application.objects.select_related(
                "candidate",
                "candidate__candidate_profile",
                "job",
                "resume",
            )
            .prefetch_related("notes")
            .filter(job__employer=self.request.user)
        )
        job_id = self.request.query_params.get("job")
        status = self.request.query_params.get("status")

        if job_id:
            queryset = queryset.filter(job_id=job_id)

        if status:
            queryset = queryset.filter(status=status)

        return queryset


class ApplicationStatusUpdateView(UpdateAPIView):
    """Update an application status when the employer owns the job."""

    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [IsEmployer, IsJobOwner]

    def get_queryset(self):
        return (
            Application.objects.select_related(
                "candidate",
                "job",
                "job__employer",
            )
            .filter(job__employer=self.request.user)
        )

    def check_object_permissions(self, request, obj):
        for permission in self.get_permissions():
            target = obj.job if isinstance(permission, IsJobOwner) else obj

            if not permission.has_object_permission(request, self, target):
                self.permission_denied(
                    request,
                    message=getattr(permission, "message", None),
                    code=getattr(permission, "code", None),
                )

    def perform_update(self, serializer):
        application = serializer.save()
        send_status_update_email(
            application.candidate,
            application,
            application.job,
        )


class ApplicationDetailView(RetrieveAPIView):
    """Return application details for the owner candidate or job employer."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            Application.objects.select_related(
                "candidate",
                "candidate__candidate_profile",
                "job",
                "job__category",
                "job__employer",
                "job__employer__employer_profile",
                "resume",
            )
            .prefetch_related("notes")
        )
        user = self.request.user

        if user.role == "EMPLOYER":
            return queryset.filter(job__employer=user)

        if user.role == "CANDIDATE":
            return queryset.filter(candidate=user)

        return queryset.none()

    def get_serializer_class(self):
        if self.request.user.role == "EMPLOYER":
            return EmployerApplicationSerializer

        return ApplicationDetailSerializer


