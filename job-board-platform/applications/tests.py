from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CandidateProfile, EmployerProfile
from applications.models import Application, Resume
from jobs.models import JobCategory, JobListing


User = get_user_model()


class JobBoardTestMixin:
    """Provide small factory helpers for job board API tests."""

    def create_candidate(self, email="candidate@example.com"):
        user = User.objects.create_user(
            email=email,
            username=email.split("@")[0],
            password="StrongPass123",
            role=User.Role.CANDIDATE,
        )
        CandidateProfile.objects.create(
            user=user,
            headline="Django Developer",
            skills="Python,Django,REST",
        )

        return user

    def create_employer(self, email="employer@example.com"):
        user = User.objects.create_user(
            email=email,
            username=email.split("@")[0],
            password="StrongPass123",
            role=User.Role.EMPLOYER,
        )
        EmployerProfile.objects.create(
            user=user,
            company_name=f"{user.username.title()} Company",
            company_description="A test company.",
            industry="Technology",
            company_size=EmployerProfile.CompanySize.STARTUP,
            location="Nairobi",
        )

        return user

    def create_category(self, name="Software Development"):
        return JobCategory.objects.create(
            name=name,
            description=f"{name} jobs.",
        )

    def create_job(self, employer, category, **overrides):
        data = {
            "employer": employer,
            "category": category,
            "title": "Backend Developer",
            "description": "Build APIs with Django.",
            "requirements": "Python and Django experience.",
            "location": "Nairobi",
            "is_remote": False,
            "job_type": JobListing.JobType.FULL_TIME,
            "experience_level": JobListing.ExperienceLevel.MID,
            "salary_min": "80000.00",
            "salary_max": "120000.00",
            "is_featured": False,
            "status": JobListing.Status.ACTIVE,
            "application_deadline": timezone.localdate() + timedelta(days=30),
        }
        data.update(overrides)

        return JobListing.objects.create(**data)

    def create_resume(self, candidate, title="Main Resume"):
        return Resume.objects.create(
            candidate=candidate,
            title=title,
            file=SimpleUploadedFile(
                "resume.pdf",
                b"%PDF-1.4 resume",
                content_type="application/pdf",
            ),
        )

    def get_results(self, response):
        data = response.data

        if isinstance(data, dict) and "results" in data:
            return data["results"]

        return data


class ResumeUploadTest(JobBoardTestMixin, APITestCase):
    """Test candidate resume upload behavior."""

    def setUp(self):
        self.candidate = self.create_candidate()
        self.employer = self.create_employer()
        self.url = reverse("applications:resume-upload")

    def test_candidate_can_upload_pdf_resume(self):
        """Candidate users can upload a valid PDF resume file."""
        self.client.force_authenticate(user=self.candidate)
        file = SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4 valid resume",
            content_type="application/pdf",
        )

        response = self.client.post(
            self.url,
            {"title": "PDF Resume", "file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resume.objects.count(), 1)
        self.assertEqual(Resume.objects.first().candidate, self.candidate)

    def test_file_larger_than_five_mb_is_rejected(self):
        """Resume files larger than 5 MB return a 400 response."""
        self.client.force_authenticate(user=self.candidate)
        file = SimpleUploadedFile(
            "large.pdf",
            b"a" * ((5 * 1024 * 1024) + 1),
            content_type="application/pdf",
        )

        response = self.client.post(
            self.url,
            {"title": "Large Resume", "file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Resume.objects.count(), 0)

    def test_invalid_file_extension_is_rejected(self):
        """Resume files that are not PDF or DOCX return a 400 response."""
        self.client.force_authenticate(user=self.candidate)
        file = SimpleUploadedFile(
            "resume.txt",
            b"plain text resume",
            content_type="text/plain",
        )

        response = self.client.post(
            self.url,
            {"title": "Text Resume", "file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Resume.objects.count(), 0)

    def test_employer_cannot_upload_resume(self):
        """Employer users cannot upload resume files."""
        self.client.force_authenticate(user=self.employer)
        file = SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4 valid resume",
            content_type="application/pdf",
        )

        response = self.client.post(
            self.url,
            {"title": "Employer Resume", "file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Resume.objects.count(), 0)


class ApplicationCreateTest(JobBoardTestMixin, APITestCase):
    """Test candidate job application creation behavior."""

    def setUp(self):
        self.candidate = self.create_candidate()
        self.employer = self.create_employer()
        self.category = self.create_category()
        self.job = self.create_job(self.employer, self.category)
        self.resume = self.create_resume(self.candidate)
        self.url = reverse("applications:application-create")

    def post_application(self, job):
        payload = {
            "job": job.id,
            "resume": self.resume.id,
            "cover_letter": "I am interested in this role.",
        }

        return self.client.post(self.url, payload, format="json")

    @patch("applications.views.send_new_application_notification")
    @patch("applications.views.send_application_confirmation_email")
    def test_candidate_can_apply_for_active_job(
        self,
        confirmation_email,
        employer_email,
    ):
        """Candidate users can apply for an active non-expired job."""
        self.client.force_authenticate(user=self.candidate)

        response = self.post_application(self.job)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Application.objects.count(), 1)
        self.assertEqual(Application.objects.first().candidate, self.candidate)
        confirmation_email.assert_called_once()
        employer_email.assert_called_once()

    def test_duplicate_application_is_rejected(self):
        """Candidates cannot apply to the same job more than once."""
        Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            resume=self.resume,
        )
        self.client.force_authenticate(user=self.candidate)

        response = self.post_application(self.job)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Application.objects.count(), 1)

    def test_applying_to_closed_job_is_rejected(self):
        """Applications to closed jobs return a 400 response."""
        closed_job = self.create_job(
            self.employer,
            self.category,
            title="Closed Job",
            status=JobListing.Status.CLOSED,
        )
        self.client.force_authenticate(user=self.candidate)

        response = self.post_application(closed_job)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Application.objects.count(), 0)

    def test_applying_to_expired_job_is_rejected(self):
        """Applications to jobs past their deadline return a 400 response."""
        expired_job = self.create_job(
            self.employer,
            self.category,
            title="Expired Job",
            application_deadline=timezone.localdate() - timedelta(days=1),
        )
        self.client.force_authenticate(user=self.candidate)

        response = self.post_application(expired_job)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Application.objects.count(), 0)


class ApplicationStatusUpdateTest(JobBoardTestMixin, APITestCase):
    """Test employer application status update behavior."""

    def setUp(self):
        self.candidate = self.create_candidate()
        self.employer = self.create_employer()
        self.category = self.create_category()
        self.job = self.create_job(self.employer, self.category)
        self.resume = self.create_resume(self.candidate)
        self.application = Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            resume=self.resume,
        )
        self.url = reverse(
            "applications:application-status-update",
            kwargs={"pk": self.application.pk},
        )

    @patch("applications.views.send_status_update_email")
    def test_employer_can_update_application_status(self, status_email):
        """The job owner can move an application to a valid next status."""
        self.client.force_authenticate(user=self.employer)

        response = self.client.patch(
            self.url,
            {"status": Application.Status.REVIEWING},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.Status.REVIEWING)
        status_email.assert_called_once()

    def test_candidate_cannot_update_application_status(self):
        """Candidate users cannot update application workflow status."""
        self.client.force_authenticate(user=self.candidate)

        response = self.client.patch(
            self.url,
            {"status": Application.Status.REVIEWING},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_status_transition_is_rejected(self):
        """Invalid status transitions return a 400 response."""
        self.client.force_authenticate(user=self.employer)

        response = self.client.patch(
            self.url,
            {"status": Application.Status.OFFER},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.Status.APPLIED)


class EmployerDashboardTest(JobBoardTestMixin, APITestCase):
    """Test employer dashboard statistics."""

    def setUp(self):
        self.candidate = self.create_candidate()
        self.employer = self.create_employer()
        self.category = self.create_category()
        self.url = reverse("jobs:employer-dashboard")

    def test_stats_return_correct_total_jobs_count(self):
        """Dashboard stats include the employer's total job count."""
        self.create_job(self.employer, self.category, title="First Job")
        self.create_job(self.employer, self.category, title="Second Job")
        self.client.force_authenticate(user=self.employer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_jobs_posted"], 2)

    def test_stats_return_correct_applications_by_status_breakdown(self):
        """Dashboard stats group received applications by status."""
        job = self.create_job(self.employer, self.category)
        second_candidate = self.create_candidate("second@example.com")
        Application.objects.create(job=job, candidate=self.candidate)
        Application.objects.create(
            job=job,
            candidate=second_candidate,
            status=Application.Status.REVIEWING,
        )
        self.client.force_authenticate(user=self.employer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["applications_by_status"],
            {
                Application.Status.APPLIED: 1,
                Application.Status.REVIEWING: 1,
            },
        )

    def test_candidate_cannot_access_employer_dashboard(self):
        """Candidate users cannot access employer dashboard stats."""
        self.client.force_authenticate(user=self.candidate)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class JobSearchTest(JobBoardTestMixin, APITestCase):
    """Test public job search and filtering behavior."""

    def setUp(self):
        self.employer = self.create_employer()
        self.category = self.create_category()
        self.url = reverse("jobs:job-list")

    def test_search_by_title_returns_matching_jobs(self):
        """Search query text matches job titles."""
        self.create_job(self.employer, self.category, title="Python Engineer")
        self.create_job(self.employer, self.category, title="Product Designer")

        response = self.client.get(self.url, {"search": "Python"})
        titles = [item["title"] for item in self.get_results(response)]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(titles, ["Python Engineer"])

    def test_filter_by_job_type_returns_correct_jobs(self):
        """The job_type filter returns only matching job listings."""
        self.create_job(
            self.employer,
            self.category,
            title="Full Time Role",
            job_type=JobListing.JobType.FULL_TIME,
        )
        self.create_job(
            self.employer,
            self.category,
            title="Contract Role",
            job_type=JobListing.JobType.CONTRACT,
        )

        response = self.client.get(
            self.url,
            {"job_type": JobListing.JobType.CONTRACT},
        )
        titles = [item["title"] for item in self.get_results(response)]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(titles, ["Contract Role"])

    def test_salary_filter_returns_only_matching_range(self):
        """Salary filters return jobs inside the requested salary range."""
        self.create_job(
            self.employer,
            self.category,
            title="Inside Range",
            salary_min="90000.00",
            salary_max="110000.00",
        )
        self.create_job(
            self.employer,
            self.category,
            title="Outside Range",
            salary_min="70000.00",
            salary_max="130000.00",
        )

        response = self.client.get(
            self.url,
            {"salary_min": "80000", "salary_max": "120000"},
        )
        titles = [item["title"] for item in self.get_results(response)]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(titles, ["Inside Range"])

    def test_is_remote_filter_works_correctly(self):
        """The is_remote filter returns only remote or onsite jobs."""
        self.create_job(
            self.employer,
            self.category,
            title="Remote Role",
            is_remote=True,
        )
        self.create_job(
            self.employer,
            self.category,
            title="Onsite Role",
            is_remote=False,
        )

        response = self.client.get(self.url, {"is_remote": "true"})
        titles = [item["title"] for item in self.get_results(response)]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(titles, ["Remote Role"])


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# User stores the active custom user model returned by get_user_model.
#
# JobBoardTestMixin provides helper methods for creating users, profiles,
# categories, jobs, resumes, and paginated response results.
#
# create_candidate creates a candidate user and candidate profile because the
# application endpoints expect candidate accounts to have profiles.
#
# create_employer creates an employer user and employer profile because jobs
# belong to employers and search can use employer company names.
#
# create_category creates a valid job category required by JobListing.
#
# create_job creates a valid active job by default and accepts overrides for
# tests that need closed, expired, remote, or salary-specific jobs.
#
# create_resume creates a saved PDF resume object for application tests.
#
# get_results handles DRF paginated responses by returning the results list.
#
# ResumeUploadTest checks resume upload success, upload validation, and role
# protection.
#
# ApplicationCreateTest checks the main application business rules: active
# jobs, duplicate prevention, closed jobs, and expired jobs.
#
# ApplicationStatusUpdateTest checks that only employers can update status and
# that invalid workflow jumps are rejected.
#
# EmployerDashboardTest checks employer dashboard totals, status breakdowns,
# and role protection.
#
# JobSearchTest checks the public job list search and filters.
#
# Important decisions that were made and why
#
# APITestCase is used because these tests exercise real API requests, URL
# routing, authentication, permissions, serializers, and views together.
#
# force_authenticate is used to keep each test focused on endpoint behavior
# instead of JWT login setup.
#
# Email helper functions are patched in tests that trigger email sending so
# the tests do not depend on an SMTP server.
#
# Jobs and users are created with helper methods so each test stays short and
# easy to read.
#
# What you should read and understand before you review the code
#
# Read DRF APITestCase and APIClient.
#
# Read force_authenticate for authenticated API tests.
#
# Read Django reverse and namespaced URL names.
#
# Read unittest.mock.patch for replacing email helpers during tests.
#
# Read SimpleUploadedFile for testing file uploads.
#
# ============================================================
# END OF REVIEW
# ============================================================
