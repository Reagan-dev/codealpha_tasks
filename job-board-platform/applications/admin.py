from django.contrib import admin

from .models import Application, ApplicationNote, Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    """Admin configuration for uploaded resumes."""

    list_display = (
        "candidate",
        "title",
        "uploaded_at",
        "is_primary",
    )
    list_filter = ("is_primary", "uploaded_at")
    search_fields = (
        "candidate__email",
        "title",
    )
    ordering = ("-uploaded_at",)


class ApplicationNoteInline(admin.TabularInline):
    """Show employer private notes inside an application admin page."""

    model = ApplicationNote
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin configuration for job applications."""

    inlines = (ApplicationNoteInline,)
    list_display = (
        "job_title",
        "candidate_email",
        "status",
        "applied_at",
    )
    list_filter = (
        "status",
        "applied_at",
    )
    search_fields = (
        "job__title",
        "candidate__email",
    )
    date_hierarchy = "applied_at"
    ordering = ("-applied_at",)

    @admin.display(description="Job title")
    def job_title(self, obj):
        """Return the related job title for the admin list page."""
        return obj.job.title

    @admin.display(description="Candidate email")
    def candidate_email(self, obj):
        """Return the candidate email for the admin list page."""
        return obj.candidate.email


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# ResumeAdmin registers Resume and shows candidate, title, upload date, and
# primary-resume status.
#
# ApplicationNoteInline displays employer private notes inside the application
# admin page.
#
# ApplicationAdmin registers Application and shows the job title, candidate
# email, status, and application date.
#
# job_title returns obj.job.title so the admin list shows readable job names.
#
# candidate_email returns obj.candidate.email so admins can identify the
# applicant quickly.
#
# Important decisions that were made and why
#
# ApplicationNote uses TabularInline because notes are short repeated rows.
#
# ApplicationNote is not registered as a separate top-level admin page because
# private notes are most useful in the context of an application.
#
# date_hierarchy is added for applications so admins can browse submissions by
# date.
#
# What you should read and understand before you review the code
#
# Read Django ModelAdmin list_display and search_fields.
#
# Read TabularInline and when to use inline admin models.
#
# Read @admin.display for custom list columns.
#
# ============================================================
# END OF REVIEW
# ============================================================
