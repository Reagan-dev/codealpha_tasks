from django.db.models import Count, Sum

from applications.models import Application

from .models import JobListing


def get_employer_stats(employer_user):
    """Return dashboard statistics for one employer user."""
    jobs = JobListing.objects.filter(employer=employer_user)
    total_jobs = jobs.count()
    active_jobs = jobs.filter(status=JobListing.Status.ACTIVE).count()
    total_applications = Application.objects.filter(job__in=jobs).count()
    status_counts = (
        Application.objects.filter(job__in=jobs)
        .values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )
    applications_by_status = {
        item["status"]: item["total"]
        for item in status_counts
    }
    top_jobs = (
        jobs.annotate(application_count=Count("applications"))
        .order_by("-application_count", "title")
        .values("title", "application_count")[:5]
    )
    total_views = jobs.aggregate(total=Sum("view_count"))["total"] or 0
    average_applications = (
        total_applications / total_jobs
        if total_jobs
        else 0
    )

    return {
        "total_jobs_posted": total_jobs,
        "active_jobs": active_jobs,
        "total_applications_received": total_applications,
        "applications_by_status": applications_by_status,
        "top_jobs": [
            {
                "title": item["title"],
                "application_count": item["application_count"],
            }
            for item in top_jobs
        ],
        "total_views": total_views,
        "average_applications_per_job": average_applications,
    }


