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


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each class or function does and why it was written that way
#
# get_employer_stats returns dashboard-style statistics for one employer.
#
# jobs selects only job listings owned by the employer.
#
# total_jobs counts all jobs posted by the employer.
#
# active_jobs counts jobs whose status is ACTIVE.
#
# total_applications counts applications across all of the employer's jobs.
#
# status_counts groups applications by status and counts each group.
#
# applications_by_status converts grouped query results into a plain
# dictionary such as {"APPLIED": 4, "REVIEWING": 2}.
#
# top_jobs annotates each job with its application count, orders by that count,
# and returns the top five jobs.
#
# total_views sums view_count across the employer's jobs.
#
# average_applications divides total applications by total jobs and returns
# zero when the employer has no jobs.
#
# Important decisions that were made and why
#
# Count and Sum are used so the database does the aggregation efficiently.
#
# Division by zero is handled because a new employer may not have posted any
# jobs yet.
#
# The function returns a plain dictionary so it can be used by views,
# serializers, tests, or future reporting commands.
#
# What you should read and understand before you review the code
#
# Read Django aggregation with Count and Sum.
#
# Read values and annotate for grouped querysets.
#
# Read reverse relationship counting with related_name values.
#
# ============================================================
# END OF REVIEW
# ============================================================
