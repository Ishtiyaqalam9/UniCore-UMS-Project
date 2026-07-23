from datetime import date

from django.core.management.base import BaseCommand

from academic.models import Course, Department, Notice


class Command(BaseCommand):
    help = "Create a small set of SQLite academic demo records."

    def handle(self, *args, **options):
        departments = [
            ("CSE", "Computer Science and Engineering"),
            ("BBA", "Business Administration"),
            ("LAW", "Law"),
        ]
        created_departments = {}
        for code, name in departments:
            department, _ = Department.objects.get_or_create(code=code, defaults={"name": name})
            created_departments[code] = department

        courses = [
            ("CSE-101", "Introduction to Computing", "CSE", 1),
            ("CSE-205", "Database Management Systems", "CSE", 4),
            ("BBA-101", "Principles of Management", "BBA", 1),
            ("LAW-101", "Introduction to Law", "LAW", 1),
        ]
        for code, title, dept_code, semester in courses:
            Course.objects.get_or_create(
                code=code,
                defaults={
                    "title": title,
                    "department": created_departments[dept_code],
                    "semester": semester,
                    "credit": 3,
                },
            )

        Notice.objects.get_or_create(
            title="Welcome to UniCore UMS",
            defaults={
                "audience": "All",
                "content": "The multi-database University Management System is ready for academic operations.",
                "publish_date": date.today(),
                "active": True,
            },
        )
        self.stdout.write(self.style.SUCCESS("SQLite demo departments, courses and notice created."))
