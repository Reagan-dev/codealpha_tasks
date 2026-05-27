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



