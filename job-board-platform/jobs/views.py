from decimal import Decimal, InvalidOperation

from django.db.models import F, Q
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsEmployer, IsJobOwner

from .models import JobCategory, JobListing
from .serializers import (
    JobCategorySerializer,
    JobCreateUpdateSerializer,
    JobDetailSerializer,
    JobListSerializer,
)
from .utils import get_employer_stats


class JobCategoryListView(ListAPIView):
    """List all job categories."""

    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [AllowAny]


class JobListView(ListAPIView):
    """List jobs with filtering, salary range, location, and search."""

    serializer_class = JobListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = (
            JobListing.objects.select_related("category", "employer")
            .select_related("employer__employer_profile")
            .all()
        )
        params = self.request.query_params

        queryset = self._filter_exact_fields(queryset, params)
        queryset = self._filter_boolean_fields(queryset, params)
        queryset = self._filter_salary_range(queryset, params)
        queryset = self._filter_location(queryset, params)
        queryset = self._filter_search(queryset, params)

        return queryset

    def _filter_exact_fields(self, queryset, params):
        filters = {}

        for field in ("category", "job_type", "experience_level"):
            value = params.get(field)

            if value:
                filters[field] = value

        return queryset.filter(**filters)

    def _filter_boolean_fields(self, queryset, params):
        for field in ("is_remote", "is_featured"):
            value = params.get(field)

            if value is None:
                continue

            queryset = queryset.filter(**{field: self._parse_bool(value)})

        return queryset

    def _filter_salary_range(self, queryset, params):
        salary_min = params.get("salary_min")
        salary_max = params.get("salary_max")

        if salary_min:
            queryset = queryset.filter(
                salary_min__gte=self._parse_decimal(
                    salary_min,
                    "salary_min",
                )
            )

        if salary_max:
            queryset = queryset.filter(
                salary_max__lte=self._parse_decimal(
                    salary_max,
                    "salary_max",
                )
            )

        return queryset

    def _filter_location(self, queryset, params):
        location = params.get("location")

        if not location:
            return queryset

        return queryset.filter(location__icontains=location)

    def _filter_search(self, queryset, params):
        search = params.get("search")

        if not search:
            return queryset

        return queryset.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(employer__employer_profile__company_name__icontains=search)
        )

    def _parse_bool(self, value):
        normalized_value = value.lower()

        if normalized_value in ("true", "1", "yes"):
            return True

        if normalized_value in ("false", "0", "no"):
            return False

        raise ValidationError(
            {"boolean": "Use true or false for boolean filters."}
        )

    def _parse_decimal(self, value, field_name):
        try:
            return Decimal(value)
        except InvalidOperation as exc:
            raise ValidationError(
                {field_name: "Enter a valid number."}
            ) from exc


class JobDetailView(RetrieveAPIView):
    """Return one job and increase its view count."""

    queryset = (
        JobListing.objects.select_related("category", "employer")
        .select_related("employer__employer_profile")
        .all()
    )
    serializer_class = JobDetailSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        self.get_queryset().filter(pk=kwargs["pk"]).update(
            view_count=F("view_count") + 1
        )

        return super().retrieve(request, *args, **kwargs)


class JobCreateView(CreateAPIView):
    """Create a job listing for the authenticated employer."""

    serializer_class = JobCreateUpdateSerializer
    permission_classes = [IsEmployer]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)


class JobManageView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a job owned by the employer."""

    serializer_class = JobCreateUpdateSerializer
    permission_classes = [IsEmployer, IsJobOwner]

    def get_queryset(self):
        return JobListing.objects.filter(employer=self.request.user)


class EmployerDashboardView(APIView):
    """Return dashboard statistics for the authenticated employer."""

    permission_classes = [IsEmployer]

    def get(self, request):
        return Response(get_employer_stats(request.user))


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# JobCategoryListView returns all job categories for dropdowns or filters.
#
# JobListView returns job listings and applies query-string filters.
#
# get_queryset builds one queryset and applies exact filters, boolean filters,
# salary filters, location filtering, and search filtering.
#
# _filter_exact_fields handles category, job_type, and experience_level
# because those match direct model fields.
#
# _filter_boolean_fields handles is_remote and is_featured separately so text
# query parameters are converted to real booleans.
#
# _filter_salary_range validates salary_min and salary_max before filtering.
#
# _filter_location uses icontains so location matching is case-insensitive.
#
# _filter_search searches title, description, and employer company name.
#
# JobDetailView returns one full job listing and increments view_count with F.
#
# JobCreateView creates jobs and sets employer to request.user.
#
# JobManageView lets employers retrieve, update, or delete only their jobs.
#
# EmployerDashboardView returns the dictionary from get_employer_stats.
#
# Important decisions that were made and why
#
# F("view_count") + 1 is used so the database increments the counter safely.
#
# Invalid boolean and salary filters return 400 errors instead of breaking the
# queryset later.
#
# JobManageView filters by employer and also uses IsJobOwner for an explicit
# object-level ownership check.
#
# What you should read and understand before you review the code
#
# Read DRF ListAPIView, RetrieveAPIView, CreateAPIView, and
# RetrieveUpdateDestroyAPIView.
#
# Read Django Q objects for OR search queries.
#
# Read F expressions for safe database-side updates.
#
# Read query parameter filtering with request.query_params.
#
# ============================================================
# END OF REVIEW
# ============================================================
