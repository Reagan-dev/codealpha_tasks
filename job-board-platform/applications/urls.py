from django.urls import path

from .views import (
    ApplicationCreateView,
    ApplicationDetailView,
    ApplicationStatusUpdateView,
    CandidateApplicationListView,
    EmployerApplicationListView,
    ResumeDeleteView,
    ResumeListView,
    ResumeUploadView,
)


app_name = "applications"

urlpatterns = [
    path(
        "resumes/",
        ResumeListView.as_view(),
        name="resume-list",
    ),
    path(
        "resumes/upload/",
        ResumeUploadView.as_view(),
        name="resume-upload",
    ),
    path(
        "resumes/<int:pk>/delete/",
        ResumeDeleteView.as_view(),
        name="resume-delete",
    ),
    path(
        "apply/",
        ApplicationCreateView.as_view(),
        name="application-create",
    ),
    path(
        "candidate/",
        CandidateApplicationListView.as_view(),
        name="candidate-application-list",
    ),
    path(
        "employer/",
        EmployerApplicationListView.as_view(),
        name="employer-application-list",
    ),
    path(
        "<int:pk>/",
        ApplicationDetailView.as_view(),
        name="application-detail",
    ),
    path(
        "<int:pk>/status/",
        ApplicationStatusUpdateView.as_view(),
        name="application-status-update",
    ),
]


