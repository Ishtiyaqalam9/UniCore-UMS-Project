from accounts.decorators import admin_required
from django.shortcuts import render

from academic.models import Course, Enrollment, Notice, StudentFee
from library.mongo import book_issues, books, is_available
from student.models import Student
from teacher.models import Teacher


def _safe_count(queryset):
    try:
        return queryset.count(), True
    except Exception:
        return 0, False


@admin_required
def home(request):
    student_count, mysql_online = _safe_count(Student.objects.all())
    teacher_count, postgres_online = _safe_count(Teacher.objects.all())
    mongo_online = is_available()
    book_count = 0
    issued_count = 0
    if mongo_online:
        try:
            book_count = books.count_documents({})
            issued_count = book_issues.count_documents({"status": "Issued"})
        except Exception:
            mongo_online = False

    fee_due = 0
    try:
        fee_due = sum((fee.balance for fee in StudentFee.objects.exclude(status="Paid")), 0)
    except Exception:
        pass

    context = {
        "student_count": student_count,
        "teacher_count": teacher_count,
        "book_count": book_count,
        "issued_count": issued_count,
        "course_count": Course.objects.filter(active=True).count(),
        "enrollment_count": Enrollment.objects.count(),
        "fee_due": fee_due,
        "notices": Notice.objects.filter(active=True)[:5],
        "mysql_online": mysql_online,
        "postgres_online": postgres_online,
        "mongo_online": mongo_online,
        "sqlite_online": True,
    }
    return render(request, "home/home.html", context)
