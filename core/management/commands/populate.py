"""Populate the database with sample users, jobs, skills, and applications."""

from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Application, CompanyProfile, Job, Skill
from user.models import User


class Command(BaseCommand):
    help = "Populate the database with deterministic sample data for local testing"

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("Starting data population...")

            skills = [
                "Python",
                "Django",
                "JavaScript",
                "React",
                "SQL",
                "AWS",
            ]
            skill_objects = {}
            for name in skills:
                skill_obj, created = Skill.objects.get_or_create(name=name)
                skill_objects[name] = skill_obj
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created skill: {name}"))

            employers_data = [
                {
                    "email": "hiring@techsolutions.com",
                    "username": "techsolutions",
                    "role": User.RoleChoice.EMP,
                    "company": "Tech Solutions",
                    "password": "testpass123",
                    "profile": {
                        "description": "Innovative software consultancy specialising in web platforms.",
                        "website": "https://techsolutions.example.com",
                    },
                },
                {
                    "email": "careers@datahub.io",
                    "username": "datahub",
                    "role": User.RoleChoice.EMP,
                    "company": "DataHub",
                    "password": "testpass123",
                    "profile": {
                        "description": "Data analytics company building insights for global brands.",
                        "website": "https://datahub.example.com",
                    },
                },
            ]

            candidates_data = [
                {
                    "email": "jane.doe@example.com",
                    "username": "janedoe",
                    "role": User.RoleChoice.CAN,
                    "password": "testpass123",
                    "resume_filename": "jane_doe_resume.txt",
                    "resume_content": "Jane Doe resume content for testing purposes.",
                },
                {
                    "email": "john.smith@example.com",
                    "username": "johnsmith",
                    "role": User.RoleChoice.CAN,
                    "password": "testpass123",
                    "resume_filename": "john_smith_resume.txt",
                    "resume_content": "John Smith resume content for testing purposes.",
                },
            ]

            def create_user_if_missing(user_payload):
                payload = {key: value for key, value in user_payload.items()}
                profile_data = payload.pop("profile", None)
                password = payload.pop("password", None)
                resume_filename = payload.pop("resume_filename", None)
                resume_content = payload.pop("resume_content", None)

                existing = User.objects.filter(email=payload["email"]).first()
                if existing:
                    return existing, False, profile_data

                if resume_filename and resume_content:
                    payload["resume"] = ContentFile(
                        resume_content.encode("utf-8"),
                        name=resume_filename,
                    )

                user = User.objects.create_user(password=password, **payload)

                return user, True, profile_data

            created_users = {}
            employer_profiles = {}

            for employer in employers_data:
                user, created, profile = create_user_if_missing(employer)
                created_users[user.email] = user
                employer_profiles[user.email] = profile or {}
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created employer: {user.email}"))

            for candidate in candidates_data:
                user, created, _ = create_user_if_missing(candidate)
                created_users[user.email] = user
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created candidate: {user.email}"))

            for email, profile in employer_profiles.items():
                if not profile:
                    continue
                employer = created_users[email]
                CompanyProfile.objects.update_or_create(
                    user=employer,
                    defaults={
                        "description": profile.get("description", ""),
                        "website": profile.get("website", ""),
                    },
                )

            jobs_data = [
                {
                    "position": "Senior Django Developer",
                    "description": "Lead backend development for client projects.",
                    "requirements": ["Python", "Django", "AWS"],
                    "salary": Decimal("95000.00"),
                    "is_active": True,
                    "employer_email": "hiring@techsolutions.com",
                },
                {
                    "position": "Full Stack Engineer",
                    "description": "Build data visualisation dashboards.",
                    "requirements": ["Python", "React", "SQL"],
                    "salary": Decimal("88000.00"),
                    "is_active": True,
                    "employer_email": "careers@datahub.io",
                },
            ]

            job_lookup = {}

            for job_spec in jobs_data:
                employer = created_users[job_spec["employer_email"]]
                job, created = Job.objects.get_or_create(
                    position=job_spec["position"],
                    employer=employer,
                    defaults={
                        "description": job_spec["description"],
                        "salary": job_spec["salary"],
                        "is_active": job_spec["is_active"],
                    },
                )

                if not created:
                    job.description = job_spec["description"]
                    job.salary = job_spec["salary"]
                    job.is_active = job_spec["is_active"]
                    job.save()

                job.requirements.set(
                    [skill_objects[name] for name in job_spec["requirements"]]
                )
                job_lookup[(job_spec["position"], job_spec["employer_email"])] = job

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created job: {job.position}"))

            applications_data = [
                {
                    "candidate_email": "jane.doe@example.com",
                    "job_position": "Senior Django Developer",
                    "employer_email": "hiring@techsolutions.com",
                    "cover_letter": "Excited to contribute my Django expertise to your projects.",
                },
                {
                    "candidate_email": "john.smith@example.com",
                    "job_position": "Full Stack Engineer",
                    "employer_email": "careers@datahub.io",
                    "cover_letter": "Experienced in building analytical dashboards for enterprises.",
                },
            ]

            for application_spec in applications_data:
                job = job_lookup[
                    (application_spec["job_position"], application_spec["employer_email"])
                ]
                candidate = created_users[application_spec["candidate_email"]]
                application, created = Application.objects.get_or_create(
                    job=job,
                    candidate=candidate,
                    defaults={"cover_letter": application_spec["cover_letter"]},
                )

                if not created:
                    application.cover_letter = application_spec["cover_letter"]
                    application.save()

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created application for {candidate.email} -> {job.position}"
                        )
                    )

            self.stdout.write(self.style.SUCCESS("Database population completed."))