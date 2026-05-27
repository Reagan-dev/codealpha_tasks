from django.contrib import admin

from .models import JobCategory, JobListing


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for job categories."""

    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    """Admin configuration for job listings."""

    list_display = (
        "title",
        "employer_company",
        "category",
        "job_type",
        "status",
        "is_featured",
        "view_count",
        "created_at",
    )
    list_filter = (
        "status",
        "job_type",
        "experience_level",
        "is_featured",
        "category",
    )
    search_fields = (
        "title",
        "employer__employer_profile__company_name",
    )
    actions = (
        "mark_as_featured",
        "mark_as_closed",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    @admin.display(description="Employer company")
    def employer_company(self, obj):
        """Return the employer company name for the admin list page."""
        profile = getattr(obj.employer, "employer_profile", None)

        if profile is None:
            return obj.employer.email

        return profile.company_name

    @admin.action(description="Mark selected jobs as featured")
    def mark_as_featured(self, request, queryset):
        """Mark selected job listings as featured."""
        queryset.update(is_featured=True)

    @admin.action(description="Mark selected jobs as closed")
    def mark_as_closed(self, request, queryset):
        """Mark selected job listings as closed."""
        queryset.update(status=JobListing.Status.CLOSED)


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# JobCategoryAdmin registers JobCategory with basic list and search behavior.
#
# JobListingAdmin registers JobListing with columns useful to employers and
# admins: title, company, category, type, status, featured flag, views, and
# created date.
#
# employer_company returns the related employer profile's company name. If the
# employer has no company profile yet, it falls back to the user's email.
#
# mark_as_featured is a bulk admin action that sets is_featured=True.
#
# mark_as_closed is a bulk admin action that changes selected jobs to CLOSED.
#
# Important decisions that were made and why
#
# The company search uses employer__employer_profile__company_name because the
# EmployerProfile related_name is employer_profile.
#
# Admin actions use queryset.update for efficient bulk updates.
#
# date_hierarchy is added to make it easier to browse job listings by date.
#
# What you should read and understand before you review the code
#
# Read Django ModelAdmin list_display, list_filter, and search_fields.
#
# Read @admin.display for custom admin columns.
#
# Read @admin.action for bulk actions.
#
# ============================================================
# END OF REVIEW
# ============================================================
