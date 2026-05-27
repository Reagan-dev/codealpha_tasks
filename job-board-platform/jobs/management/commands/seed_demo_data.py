import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import CandidateProfile, EmployerProfile
from applications.models import Application, ApplicationNote, Resume
from jobs.models import JobCategory, JobListing


User = get_user_model()
PASSWORD = "TestPass123!"


class Command(BaseCommand):
    """Seed realistic demo data for the Job Board Platform."""

    help = "Seed demo employers, candidates, jobs, resumes, and applications."

    def handle(self, *args, **options):
        self._configure_output()

        if self._already_seeded():
            self.stdout.write(self.style.WARNING("Already seeded. Skipping."))
            return

        random.seed(42)

        with transaction.atomic():
            employers, employer_count = self._create_employers()
            candidates, candidate_count = self._create_candidates()
            categories, category_count = self._create_categories()
            jobs, job_count = self._create_jobs(employers, categories)
            resumes, resume_count = self._create_resumes(candidates)
            applications, application_count = self._create_applications(
                candidates,
                jobs,
                resumes,
            )
            note_count = self._create_application_notes(applications)

        self._print_summary(
            employer_count,
            candidate_count,
            category_count,
            job_count,
            resume_count,
            application_count,
            note_count,
        )

    def _configure_output(self):
        output_stream = getattr(self.stdout, "_out", None)

        if hasattr(output_stream, "reconfigure"):
            output_stream.reconfigure(encoding="utf-8")

    def _already_seeded(self):
        employer_emails = [
            "techcorp@example.com",
            "greenbiz@example.com",
            "devhive@example.com",
        ]
        candidate_emails = [
            "alice@example.com",
            "bob@example.com",
            "carol@example.com",
        ]
        job_titles = [
            "Senior Backend Engineer",
            "Junior Python Developer",
            "DevOps Engineer",
            "Product Manager",
            "Financial Analyst",
            "Marketing Specialist",
            "Data Scientist",
            "React Frontend Developer",
            "UI/UX Designer Intern",
            "Full Stack Developer",
        ]

        return (
            User.objects.filter(email__in=employer_emails).count() == 3
            and User.objects.filter(email__in=candidate_emails).count() == 3
            and JobListing.objects.filter(title__in=job_titles).count() == 10
            and Application.objects.filter(job__title__in=job_titles).count()
            == 9
        )

    def _create_employers(self):
        employer_data = [
            {
                "email": "techcorp@example.com",
                "username": "techcorp",
                "company_name": "TechCorp Kenya",
                "industry": "Technology",
                "company_size": EmployerProfile.CompanySize.MEDIUM,
                "location": "Nairobi",
            },
            {
                "email": "greenbiz@example.com",
                "username": "greenbiz",
                "company_name": "GreenBiz Africa",
                "industry": "Finance",
                "company_size": EmployerProfile.CompanySize.SMALL,
                "location": "Nairobi",
            },
            {
                "email": "devhive@example.com",
                "username": "devhive",
                "company_name": "DevHive Ltd",
                "industry": "Technology",
                "company_size": EmployerProfile.CompanySize.STARTUP,
                "location": "Remote",
            },
        ]
        employers = {}
        created_count = 0

        for data in employer_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "username": data["username"],
                    "role": User.Role.EMPLOYER,
                    "first_name": data["company_name"].split()[0],
                },
            )

            if created:
                user.set_password(PASSWORD)
                user.save(update_fields=["password"])
                created_count += 1

            EmployerProfile.objects.get_or_create(
                user=user,
                defaults={
                    "company_name": data["company_name"],
                    "company_description": self._company_description(
                        data["company_name"],
                        data["industry"],
                    ),
                    "industry": data["industry"],
                    "company_size": data["company_size"],
                    "location": data["location"],
                    "verified": True,
                },
            )
            employers[data["username"]] = user

        return employers, created_count

    def _create_candidates(self):
        candidate_data = [
            {
                "email": "alice@example.com",
                "username": "alice",
                "first_name": "Alice",
                "headline": "Senior Django Developer",
                "skills": "Python,Django,PostgreSQL,REST APIs",
                "experience_years": 5,
            },
            {
                "email": "bob@example.com",
                "username": "bob",
                "first_name": "Bob",
                "headline": "Frontend Engineer",
                "skills": "React,TypeScript,TailwindCSS",
                "experience_years": 3,
            },
            {
                "email": "carol@example.com",
                "username": "carol",
                "first_name": "Carol",
                "headline": "Data Analyst",
                "skills": "Python,Pandas,SQL,Power BI",
                "experience_years": 2,
            },
        ]
        candidates = {}
        created_count = 0

        for data in candidate_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "username": data["username"],
                    "role": User.Role.CANDIDATE,
                    "first_name": data["first_name"],
                },
            )

            if created:
                user.set_password(PASSWORD)
                user.save(update_fields=["password"])
                created_count += 1

            CandidateProfile.objects.get_or_create(
                user=user,
                defaults={
                    "headline": data["headline"],
                    "skills": data["skills"],
                    "experience_years": data["experience_years"],
                },
            )
            candidates[data["username"]] = user

        return candidates, created_count

    def _create_categories(self):
        category_names = [
            "Technology",
            "Marketing",
            "Finance",
            "Design",
            "Operations",
            "Data Science",
        ]
        categories = {}
        created_count = 0

        for name in category_names:
            category, created = JobCategory.objects.get_or_create(
                name=name,
                defaults={
                    "description": (
                        f"Jobs and career opportunities in {name}."
                    ),
                },
            )
            categories[name] = category
            created_count += int(created)

        return categories, created_count

    def _create_jobs(self, employers, categories):
        today = timezone.localdate()
        job_data = [
            {
                "employer": employers["techcorp"],
                "title": "Senior Backend Engineer",
                "category": categories["Technology"],
                "description": (
                    "Lead backend development for high-traffic hiring "
                    "products used by teams across East Africa."
                ),
                "requirements": (
                    "Strong Django, PostgreSQL, API design, testing, and "
                    "production deployment experience."
                ),
                "location": "Nairobi",
                "job_type": JobListing.JobType.FULL_TIME,
                "experience_level": JobListing.ExperienceLevel.SENIOR,
                "status": JobListing.Status.ACTIVE,
                "is_featured": True,
                "salary_min": 150000,
                "salary_max": 250000,
            },
            {
                "employer": employers["techcorp"],
                "title": "Junior Python Developer",
                "category": categories["Technology"],
                "description": (
                    "Join a backend team building internal automation tools "
                    "and customer-facing API features."
                ),
                "requirements": (
                    "Python fundamentals, Git, SQL basics, and willingness "
                    "to learn Django REST Framework."
                ),
                "location": "Nairobi",
                "job_type": JobListing.JobType.FULL_TIME,
                "experience_level": JobListing.ExperienceLevel.ENTRY,
                "status": JobListing.Status.ACTIVE,
                "salary_min": 60000,
                "salary_max": 100000,
            },
            {
                "employer": employers["techcorp"],
                "title": "DevOps Engineer",
                "category": categories["Technology"],
                "description": (
                    "Improve CI/CD, container workflows, monitoring, and "
                    "cloud reliability for production services."
                ),
                "requirements": (
                    "Docker, Linux, cloud hosting, observability, and "
                    "deployment automation experience."
                ),
                "location": "Remote",
                "is_remote": True,
                "job_type": JobListing.JobType.CONTRACT,
                "experience_level": JobListing.ExperienceLevel.MID,
                "status": JobListing.Status.ACTIVE,
                "salary_min": 120000,
                "salary_max": 180000,
            },
            {
                "employer": employers["techcorp"],
                "title": "Product Manager",
                "category": categories["Operations"],
                "description": (
                    "Own roadmap planning and delivery for hiring workflow "
                    "features across employer and candidate products."
                ),
                "requirements": (
                    "Product discovery, stakeholder management, analytics, "
                    "and agile delivery experience."
                ),
                "location": "Nairobi",
                "job_type": JobListing.JobType.FULL_TIME,
                "experience_level": JobListing.ExperienceLevel.LEAD,
                "status": JobListing.Status.CLOSED,
            },
            {
                "employer": employers["greenbiz"],
                "title": "Financial Analyst",
                "category": categories["Finance"],
                "description": (
                    "Prepare financial models, portfolio reports, and "
                    "investment insights for growth-stage businesses."
                ),
                "requirements": (
                    "Financial modeling, Excel, reporting, budgeting, and "
                    "business analysis skills."
                ),
                "location": "Nairobi",
                "job_type": JobListing.JobType.FULL_TIME,
                "experience_level": JobListing.ExperienceLevel.MID,
                "status": JobListing.Status.ACTIVE,
                "salary_min": 80000,
                "salary_max": 130000,
            },
            {
                "employer": employers["greenbiz"],
                "title": "Marketing Specialist",
                "category": categories["Marketing"],
                "description": (
                    "Plan campaigns, write conversion-focused content, and "
                    "support digital acquisition across African markets."
                ),
                "requirements": (
                    "Campaign planning, social media, content writing, and "
                    "basic analytics experience."
                ),
                "location": "Nairobi",
                "job_type": JobListing.JobType.FULL_TIME,
                "experience_level": JobListing.ExperienceLevel.ENTRY,
                "status": JobListing.Status.ACTIVE,
            },
            {
                "employer": employers["greenbiz"],
                "title": "Data Scientist",
                "category": categories["Data Science"],
                "description": (
                    "Build predictive models and dashboards that help teams "
                    "measure financial and operational performance."
                ),
                "requirements": (
                    "Python, SQL, statistics, machine learning, and clear "
                    "business communication."
                ),
                "location": "Nairobi",
                "job_type": JobListing.JobType.FULL_TIME,
                "experience_level": JobListing.ExperienceLevel.SENIOR,
                "status": JobListing.Status.ACTIVE,
                "is_featured": True,
                "salary_min": 160000,
                "salary_max": 220000,
            },
            {
                "employer": employers["devhive"],
                "title": "React Frontend Developer",
                "category": categories["Technology"],
                "description": (
                    "Build polished dashboard experiences for SaaS clients "
                    "using modern React and TypeScript."
                ),
                "requirements": (
                    "React, TypeScript, component architecture, "
                    "accessibility, and API integration experience."
                ),
                "location": "Remote",
                "is_remote": True,
                "job_type": JobListing.JobType.FULL_TIME,
                "experience_level": JobListing.ExperienceLevel.MID,
                "status": JobListing.Status.ACTIVE,
                "salary_min": 100000,
                "salary_max": 150000,
            },
            {
                "employer": employers["devhive"],
                "title": "UI/UX Designer Intern",
                "category": categories["Design"],
                "description": (
                    "Support product research, wireframes, prototypes, and "
                    "design QA for remote product teams."
                ),
                "requirements": (
                    "Portfolio with interface design work, curiosity, and "
                    "comfort using modern design tools."
                ),
                "location": "Remote",
                "is_remote": True,
                "job_type": JobListing.JobType.INTERNSHIP,
                "experience_level": JobListing.ExperienceLevel.ENTRY,
                "status": JobListing.Status.ACTIVE,
            },
            {
                "employer": employers["devhive"],
                "title": "Full Stack Developer",
                "category": categories["Technology"],
                "description": (
                    "Deliver end-to-end product features across Django APIs, "
                    "React frontends, and PostgreSQL data models."
                ),
                "requirements": (
                    "Django, React, PostgreSQL, automated testing, and "
                    "practical deployment experience."
                ),
                "location": "Nairobi",
                "job_type": JobListing.JobType.FULL_TIME,
                "experience_level": JobListing.ExperienceLevel.SENIOR,
                "status": JobListing.Status.ACTIVE,
                "salary_min": 180000,
                "salary_max": 280000,
                "application_deadline": today + timedelta(days=7),
            },
        ]
        jobs = {}
        created_count = 0

        for data in job_data:
            employer = data.pop("employer")
            title = data.pop("title")
            data.setdefault("view_count", random.randint(10, 300))
            job, created = JobListing.objects.get_or_create(
                employer=employer,
                title=title,
                defaults=data,
            )
            jobs[title] = job
            created_count += int(created)

        return jobs, created_count

    def _create_resumes(self, candidates):
        resume_data = [
            {
                "candidate": candidates["alice"],
                "title": "Alice — Django Backend Resume",
                "file": "resumes/alice_resume.pdf",
            },
            {
                "candidate": candidates["bob"],
                "title": "Bob — Frontend Portfolio Resume",
                "file": "resumes/bob_resume.pdf",
            },
            {
                "candidate": candidates["carol"],
                "title": "Carol — Data Analyst Resume",
                "file": "resumes/carol_resume.pdf",
            },
        ]
        resumes = {}
        created_count = 0

        for data in resume_data:
            resume, created = Resume.objects.get_or_create(
                candidate=data["candidate"],
                title=data["title"],
                defaults={
                    "file": data["file"],
                    "is_primary": True,
                },
            )
            resumes[data["candidate"].username] = resume
            created_count += int(created)

        return resumes, created_count

    def _create_applications(self, candidates, jobs, resumes):
        application_data = [
            (
                candidates["alice"],
                jobs["Senior Backend Engineer"],
                resumes["alice"],
                Application.Status.OFFER,
            ),
            (
                candidates["alice"],
                jobs["DevOps Engineer"],
                resumes["alice"],
                Application.Status.INTERVIEW,
            ),
            (
                candidates["alice"],
                jobs["Full Stack Developer"],
                resumes["alice"],
                Application.Status.APPLIED,
            ),
            (
                candidates["bob"],
                jobs["React Frontend Developer"],
                resumes["bob"],
                Application.Status.REVIEWING,
            ),
            (
                candidates["bob"],
                jobs["UI/UX Designer Intern"],
                resumes["bob"],
                Application.Status.APPLIED,
            ),
            (
                candidates["bob"],
                jobs["Junior Python Developer"],
                resumes["bob"],
                Application.Status.REJECTED,
            ),
            (
                candidates["carol"],
                jobs["Data Scientist"],
                resumes["carol"],
                Application.Status.INTERVIEW,
            ),
            (
                candidates["carol"],
                jobs["Financial Analyst"],
                resumes["carol"],
                Application.Status.APPLIED,
            ),
            (
                candidates["carol"],
                jobs["Marketing Specialist"],
                resumes["carol"],
                Application.Status.REVIEWING,
            ),
        ]
        applications = {}
        created_count = 0

        for candidate, job, resume, app_status in application_data:
            application, created = Application.objects.get_or_create(
                candidate=candidate,
                job=job,
                defaults={
                    "resume": resume,
                    "cover_letter": self._cover_letter(candidate, job),
                    "status": app_status,
                },
            )
            applications[(candidate.username, job.title)] = application
            created_count += int(created)

        return applications, created_count

    def _create_application_notes(self, applications):
        note_data = [
            (
                ("alice", "Senior Backend Engineer"),
                "Strong Django background. Schedule technical round.",
            ),
            (
                ("bob", "React Frontend Developer"),
                "Good portfolio. Needs system design assessment.",
            ),
            (
                ("carol", "Data Scientist"),
                "Impressive SQL test score. Fast-track to interview.",
            ),
        ]
        created_count = 0

        for application_key, note in note_data:
            application = applications[application_key]
            _, created = ApplicationNote.objects.get_or_create(
                application=application,
                note=note,
                defaults={"created_by": application.job.employer},
            )
            created_count += int(created)

        return created_count

    def _company_description(self, company_name, industry):
        return (
            f"{company_name} is a growing {industry.lower()} employer "
            "hiring skilled teams across Kenya and remote markets."
        )

    def _cover_letter(self, candidate, job):
        return (
            f"I am excited to apply for the {job.title} role and bring my "
            "skills to your team."
        )

    def _print_summary(
        self,
        employer_count,
        candidate_count,
        category_count,
        job_count,
        resume_count,
        application_count,
        note_count,
    ):
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {employer_count} employers, "
                f"{candidate_count} candidates"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f"✓ Created {category_count} job categories")
        )
        self.stdout.write(
            self.style.SUCCESS(f"✓ Created {job_count} job listings")
        )
        self.stdout.write(
            self.style.SUCCESS(f"✓ Created {resume_count} resumes")
        )
        self.stdout.write(
            self.style.SUCCESS(f"✓ Created {application_count} applications")
        )
        self.stdout.write(
            self.style.SUCCESS(f"✓ Created {note_count} application notes")
        )
        self.stdout.write(
            self.style.SUCCESS(
                "✓ Seed complete — login: techcorp@example.com / "
                "TestPass123!"
            )
        )


# ============================================================
# REVIEW — READ THIS THEN DELETE FROM THIS LINE TO THE END
# ============================================================
#
# What each section of the command does and why
#
# The imports load Django helpers, the custom user model, and the models that
# need demo rows.
#
# PASSWORD stores the shared demo password so it is written once and reused for
# every seeded user.
#
# Command is the Django management command class. Django discovers it because
# it lives in jobs/management/commands/seed_demo_data.py.
#
# _configure_output switches the command output to UTF-8 when the terminal
# supports it so the requested checkmark character can print on Windows.
#
# handle is the command entry point. It checks whether demo data already
# exists, starts a transaction, creates each group of data, and prints a
# summary.
#
# _already_seeded checks for the known demo users, jobs, and applications. If
# they all exist, the command prints "Already seeded. Skipping." and exits.
#
# _create_employers creates employer users and their EmployerProfile rows.
#
# _create_candidates creates candidate users and their CandidateProfile rows.
#
# _create_categories creates the six job categories used by the demo jobs.
#
# _create_jobs creates realistic listings for each employer and assigns view
# counts.
#
# _create_resumes creates resume database records using dummy FileField paths.
# It does not create actual files on disk.
#
# _create_applications creates candidate applications with the requested
# statuses.
#
# _create_application_notes creates private employer notes for selected
# applications.
#
# _company_description and _cover_letter keep repeated demo text generation out
# of the main creation methods.
#
# _print_summary prints the final counts and a useful employer login.
#
# Why idempotency matters and how get_or_create achieves it
#
# Idempotency matters because seed commands are often run multiple times during
# development, review, and deployment. Running the command again should not
# create duplicate users, jobs, applications, resumes, or notes.
#
# get_or_create first tries to find an existing row using stable lookup fields
# such as email, category name, employer plus job title, or candidate plus job.
# If the row exists, Django returns it. If it does not exist, Django creates it
# with the provided defaults.
#
# Why random.seed(42) is used for view counts
#
# random.seed(42) makes the random view_count values reproducible. That means
# every fresh seed run creates realistic-looking numbers, but the numbers stay
# predictable for demos, screenshots, and tests.
#
# What to verify after running the command
#
# Run python manage.py seed_demo_data and confirm it finishes without errors.
#
# Run the command a second time and confirm it prints Already seeded.
# Skipping.
#
# Open /swagger/ and call GET /api/jobs/ to confirm real jobs are returned.
#
# Log in as techcorp@example.com with TestPass123! and confirm the employer
# dashboard has non-zero job, application, and view statistics.
#
# ============================================================
# END OF REVIEW
# ============================================================
