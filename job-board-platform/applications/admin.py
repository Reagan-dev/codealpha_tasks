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


