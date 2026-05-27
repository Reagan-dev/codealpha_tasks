from django.urls import path

from .views import (
    EmployerDashboardView,
    JobCategoryListView,
    JobCreateView,
    JobDetailView,
    JobListView,
    JobManageView,
)


app_name = "jobs"

urlpatterns = [
    path(
        "categories/",
        JobCategoryListView.as_view(),
        name="category-list",
    ),
    path(
        "",
        JobListView.as_view(),
        name="job-list",
    ),
    path(
        "create/",
        JobCreateView.as_view(),
        name="job-create",
    ),
    path(
        "dashboard/",
        EmployerDashboardView.as_view(),
        name="employer-dashboard",
    ),
    path(
        "<int:pk>/",
        JobDetailView.as_view(),
        name="job-detail",
    ),
    path(
        "<int:pk>/manage/",
        JobManageView.as_view(),
        name="job-manage",
    ),
]


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# app_name sets the namespace for these routes as jobs.
#
# urlpatterns stores all job-related URL patterns.
#
# categories/ lists job categories through JobCategoryListView.
#
# The empty path lists jobs through JobListView, so /api/jobs/ is the public
# job list endpoint.
#
# create/ sends employer job creation requests to JobCreateView.
#
# dashboard/ sends employer dashboard requests to EmployerDashboardView.
#
# <int:pk>/ sends public job detail requests to JobDetailView.
#
# <int:pk>/manage/ sends owner-only retrieve, update, and delete requests to
# JobManageView.
#
# Important decisions that were made and why
#
# Public detail and employer management use different routes because they have
# different serializers and permissions.
#
# create/ and dashboard/ are listed before <int:pk>/ so Django checks named
# action routes before numeric detail routes.
#
# What you should read and understand before you review the code
#
# Read Django path converters such as <int:pk>.
#
# Read DRF generic class-based views and how as_view connects them to URLs.
#
# Read URL naming and reverse lookups such as reverse("jobs:job-detail").
#
# ============================================================
# END OF REVIEW
# ============================================================
