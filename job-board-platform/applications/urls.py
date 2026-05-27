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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# app_name sets the namespace for these routes as applications.
#
# urlpatterns stores all application and resume URL patterns.
#
# resumes/ lists the authenticated candidate's resumes.
#
# resumes/upload/ uploads a new resume for the authenticated candidate.
#
# resumes/<int:pk>/delete/ deletes one candidate-owned resume.
#
# apply/ creates a new job application for a candidate.
#
# candidate/ lists applications submitted by the authenticated candidate.
#
# employer/ lists applications received for the authenticated employer's jobs.
#
# <int:pk>/ returns one application detail record.
#
# <int:pk>/status/ updates one application's status.
#
# Important decisions that were made and why
#
# Resume routes are grouped under resumes/ so file-related endpoints are easy
# to find.
#
# Candidate and employer list routes are separate because each role sees a
# different queryset and serializer.
#
# Detail and status update routes are separate because reading an application
# and changing its workflow state are different actions.
#
# What you should read and understand before you review the code
#
# Read Django app URLconfs and app_name namespacing.
#
# Read path converters such as <int:pk>.
#
# Read how DRF views map HTTP methods to class-based view methods.
#
# ============================================================
# END OF REVIEW
# ============================================================
