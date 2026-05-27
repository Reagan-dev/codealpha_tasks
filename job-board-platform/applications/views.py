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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# ResumeUploadView lets a candidate upload a resume and sets candidate to the
# signed-in user.
#
# ResumeListView lists only resumes owned by the signed-in candidate.
#
# ResumeDeleteView deletes only a resume owned by the signed-in candidate.
#
# ApplicationCreateView creates a candidate application after checking the
# resume, job state, and duplicate application rule.
#
# _validate_resume_owner prevents candidates from applying with another
# candidate's resume.
#
# _validate_job_can_receive_application rejects closed, draft, or expired jobs.
#
# _validate_not_already_applied returns 400 when the candidate already applied.
#
# CandidateApplicationListView lists applications submitted by the candidate.
#
# EmployerApplicationListView lists applications for the employer's jobs and
# supports job and status filters.
#
# ApplicationStatusUpdateView updates status only when the employer owns the
# job connected to the application.
#
# check_object_permissions passes application.job into IsJobOwner because that
# permission checks ownership on JobListing objects.
#
# perform_update sends the candidate a status update email after saving.
#
# ApplicationDetailView returns employer detail data to employers and
# candidate detail data to candidates.
#
# Important decisions that were made and why
#
# Candidate and employer list views filter by request.user so users cannot see
# records that belong to someone else.
#
# ApplicationCreateView performs business-rule checks in the view because they
# depend on the current authenticated user.
#
# Email helpers are called after the application or status change is saved so
# the email describes a real database change.
#
# ApplicationDetailView restricts the queryset by role before serialization so
# authenticated users cannot fetch unrelated applications.
#
# What you should read and understand before you review the code
#
# Read DRF perform_create and perform_update hooks.
#
# Read queryset filtering for object-level data access.
#
# Read unique_together on Application and why the view also returns a clear
# 400 error before the database constraint is hit.
#
# Read custom object permissions and how check_object_permissions works.
#
# ============================================================
# END OF REVIEW
# ============================================================
