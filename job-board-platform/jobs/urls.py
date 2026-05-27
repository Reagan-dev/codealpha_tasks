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


