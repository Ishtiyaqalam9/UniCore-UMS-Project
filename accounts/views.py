from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from pymongo.errors import PyMongoError

from academic.models import (
    Attendance,
    BusCardApplication,
    ClassRoutine,
    Course,
    CourseAssignment,
    Enrollment,
    Notice,
    Result,
    StudentFee,
)
from library.mongo import book_issues, is_available
from student.models import Student
from teacher.models import Teacher

from .decorators import admin_required, student_required, teacher_required
from .forms import AccountCreateForm, AccountPasswordForm, StudentBusCardForm
from .models import UserProfile
from .utils import get_user_profile, get_user_role


def _current_academic_year():
    today = timezone.localdate()
    start_year = today.year if today.month >= 7 else today.year - 1
    return f"{start_year}-{start_year + 1}"


def _student_identity(user):
    profile = get_user_profile(user)
    reference = profile.reference_id
    student = None
    database_online = True
    try:
        student = Student.objects.filter(student_id=reference).first()
        if student is None and str(reference).isdigit():
            student = Student.objects.filter(pk=int(reference)).first()
    except Exception:
        database_online = False
    display_name = student.name if student else (profile.display_name or user.username)
    return profile, reference, student, database_online, display_name


def _teacher_identity(user):
    profile = get_user_profile(user)
    reference = profile.reference_id
    teacher = None
    database_online = True
    try:
        teacher = Teacher.objects.filter(employee_id=reference).first()
        if teacher is None and str(reference).isdigit():
            teacher = Teacher.objects.filter(pk=int(reference)).first()
    except Exception:
        database_online = False
    display_name = teacher.name if teacher else (profile.display_name or user.username)
    return profile, reference, teacher, database_online, display_name


def _member_library_summary(reference):
    records = []
    active_count = 0
    online = is_available()
    if online:
        try:
            query = {"$or": [{"borrower_ref": reference}, {"student_ref": reference}]}
            active_count = book_issues.count_documents({"$and": [query, {"status": "Issued"}]})
            for record in book_issues.find(query).sort("issue_date", -1).limit(5):
                record["id"] = str(record["_id"])
                records.append(record)
        except PyMongoError:
            online = False
            active_count = 0
            records = []
    return online, active_count, records


@login_required
def portal_redirect(request):
    role = get_user_role(request.user)
    if role == UserProfile.STUDENT:
        return redirect("student_portal")
    if role == UserProfile.TEACHER:
        return redirect("teacher_portal")
    if role == UserProfile.ADMIN:
        return redirect("home")
    messages.error(request, "Your account has no assigned role. Contact the administrator.")
    return redirect("login")


@admin_required
def account_list(request):
    accounts = User.objects.select_related("ums_profile").all().order_by("username")
    query = request.GET.get("q", "").strip()
    role = request.GET.get("role", "").strip()
    if query:
        accounts = accounts.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(ums_profile__display_name__icontains=query)
            | Q(ums_profile__reference_id__icontains=query)
        ).distinct()
    if role == UserProfile.ADMIN:
        accounts = accounts.filter(Q(is_staff=True) | Q(ums_profile__role=UserProfile.ADMIN)).distinct()
    elif role in {UserProfile.STUDENT, UserProfile.TEACHER}:
        accounts = accounts.filter(ums_profile__role=role)

    labels = dict(UserProfile.ROLE_CHOICES)
    rows = []
    for account in accounts:
        try:
            profile = account.ums_profile
        except UserProfile.DoesNotExist:
            profile = None
        account_role = get_user_role(account)
        rows.append(
            {
                "user": account,
                "profile": profile,
                "role": account_role,
                "role_label": labels.get(account_role, "Unassigned"),
                "display_name": (profile.display_name if profile else "")
                or account.get_full_name()
                or account.username,
                "reference_id": profile.reference_id if profile else "",
            }
        )
    return render(
        request,
        "accounts/account_list.html",
        {"rows": rows, "query": query, "selected_role": role, "role_choices": UserProfile.ROLE_CHOICES},
    )


@admin_required
def account_create(request):
    form = AccountCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"Login account created for {user.username}.")
        return redirect("account_list")
    return render(request, "accounts/account_form.html", {"form": form, "title": "Create Login Account"})


@admin_required
def account_password_reset(request, user_id):
    account = get_object_or_404(User, pk=user_id)
    form = AccountPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        account.set_password(form.cleaned_data["password1"])
        account.save(update_fields=["password"])
        messages.success(request, f"Password reset for {account.username}.")
        return redirect("account_list")
    return render(
        request,
        "accounts/account_form.html",
        {"form": form, "title": f"Reset Password: {account.username}"},
    )


@admin_required
def account_toggle(request, user_id):
    if request.method == "POST":
        account = get_object_or_404(User, pk=user_id)
        if account == request.user:
            messages.warning(request, "You cannot deactivate your own account.")
        else:
            account.is_active = not account.is_active
            account.save(update_fields=["is_active"])
            state = "activated" if account.is_active else "deactivated"
            messages.success(request, f"{account.username} was {state}.")
    return redirect("account_list")


@admin_required
def account_delete(request, user_id):
    account = get_object_or_404(User, pk=user_id)
    if account == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("account_list")
    if request.method == "POST":
        username = account.username
        account.delete()
        messages.success(request, f"Account {username} deleted.")
        return redirect("account_list")
    return render(request, "accounts/account_confirm_delete.html", {"account": account})


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    for field in form.fields.values():
        field.widget.attrs["class"] = "form-control"
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Your password was changed successfully.")
        return redirect("portal_redirect")
    return render(request, "accounts/account_form.html", {"form": form, "title": "Change Password"})


@student_required
def student_portal(request):
    profile, reference, student, database_online, display_name = _student_identity(request.user)
    enrollments = Enrollment.objects.filter(student_ref=reference).select_related("course", "course__department")
    attendance = Attendance.objects.filter(enrollment__student_ref=reference)
    results = Result.objects.filter(enrollment__student_ref=reference)
    fees = StudentFee.objects.filter(student_ref=reference)
    notices = Notice.objects.filter(active=True, audience__in=["All", "Students"])[:5]

    attendance_totals = attendance.values("status").annotate(total=Count("id"))
    summary = {item["status"]: item["total"] for item in attendance_totals}
    total_attendance = sum(summary.values())
    present_equivalent = summary.get(Attendance.PRESENT, 0) + (summary.get(Attendance.LATE, 0) * 0.5)
    attendance_rate = round((present_equivalent / total_attendance) * 100, 1) if total_attendance else 0
    mongo_online, active_book_count, recent_books = _member_library_summary(reference)
    bus_card = BusCardApplication.objects.filter(student_ref=reference).order_by("-created_at").first()

    context = {
        "profile": profile,
        "student": student,
        "database_online": database_online,
        "display_name": display_name,
        "enrollment_count": enrollments.count(),
        "result_count": results.count(),
        "attendance_rate": attendance_rate,
        "fee_balance": sum((item.balance for item in fees), Decimal("0")),
        "notices": notices,
        "recent_enrollments": enrollments[:4],
        "recent_results": results.select_related("enrollment__course")[:5],
        "mongo_online": mongo_online,
        "active_book_count": active_book_count,
        "recent_books": recent_books,
        "bus_card": bus_card,
    }
    return render(request, "accounts/student_portal.html", context)


@student_required
def student_profile(request):
    profile, reference, student, database_online, display_name = _student_identity(request.user)
    return render(
        request,
        "accounts/student_profile.html",
        {
            "profile": profile,
            "student": student,
            "database_online": database_online,
            "display_name": display_name,
        },
    )


@student_required
def student_courses(request):
    profile, reference, student, database_online, display_name = _student_identity(request.user)
    enrollments = Enrollment.objects.filter(student_ref=reference).select_related("course", "course__department")
    return render(
        request,
        "accounts/student_courses.html",
        {
            "profile": profile,
            "student": student,
            "database_online": database_online,
            "display_name": display_name,
            "enrollments": enrollments,
        },
    )


@student_required
def student_course_registration(request):
    profile, reference, student, database_online, display_name = _student_identity(request.user)
    academic_year = _current_academic_year()
    existing = Enrollment.objects.filter(student_ref=reference, academic_year=academic_year)

    available = Course.objects.filter(active=True).select_related("department")
    if student:
        available = available.filter(semester=student.semester)
    existing_course_ids = existing.values_list("course_id", flat=True)
    available = available.exclude(pk__in=existing_course_ids)

    if request.method == "POST":
        course = get_object_or_404(Course, pk=request.POST.get("course_id"), active=True)
        if student and course.semester != student.semester:
            messages.error(request, "You can register only for courses offered in your current semester.")
            return redirect("student_course_registration")
        _, created = Enrollment.objects.get_or_create(
            student_ref=reference,
            course=course,
            academic_year=academic_year,
            semester=course.semester,
            defaults={"student_name": display_name},
        )
        if created:
            messages.success(request, f"You are now enrolled in {course.code} — {course.title}.")
        else:
            messages.info(request, "You are already enrolled in this course.")
        return redirect("student_course_registration")

    course_rows = []
    dept_text = (student.dept if student else "").lower()
    for course in available:
        is_recommended = bool(
            dept_text
            and (
                course.department.code.lower() in dept_text
                or course.department.name.lower() in dept_text
                or dept_text in course.department.name.lower()
            )
        )
        course_rows.append({"course": course, "recommended": is_recommended})
    course_rows.sort(key=lambda row: (not row["recommended"], row["course"].code))

    return render(
        request,
        "accounts/student_course_registration.html",
        {
            "profile": profile,
            "student": student,
            "display_name": display_name,
            "academic_year": academic_year,
            "existing": existing.select_related("course"),
            "course_rows": course_rows,
        },
    )


@student_required
def student_drop_course(request, enrollment_id):
    if request.method != "POST":
        return redirect("student_courses")
    profile = get_user_profile(request.user)
    enrollment = get_object_or_404(Enrollment, pk=enrollment_id, student_ref=profile.reference_id)
    if enrollment.attendance_records.exists() or enrollment.results.exists():
        messages.error(request, "This course cannot be withdrawn because academic records already exist.")
    else:
        course_code = enrollment.course.code
        enrollment.delete()
        messages.success(request, f"{course_code} was removed from your registered courses.")
    return redirect("student_courses")


@student_required
def student_attendance_summary(request):
    profile, reference, student, database_online, display_name = _student_identity(request.user)
    enrollments = Enrollment.objects.filter(student_ref=reference).select_related("course")
    records = Attendance.objects.filter(enrollment__student_ref=reference).select_related("enrollment__course")
    rows = []
    for enrollment in enrollments:
        course_records = records.filter(enrollment=enrollment)
        totals = {item["status"]: item["total"] for item in course_records.values("status").annotate(total=Count("id"))}
        total = sum(totals.values())
        earned = totals.get(Attendance.PRESENT, 0) + totals.get(Attendance.LATE, 0) * 0.5
        rows.append(
            {
                "enrollment": enrollment,
                "present": totals.get(Attendance.PRESENT, 0),
                "absent": totals.get(Attendance.ABSENT, 0),
                "late": totals.get(Attendance.LATE, 0),
                "total": total,
                "rate": round((earned / total) * 100, 1) if total else 0,
            }
        )
    return render(
        request,
        "accounts/student_attendance.html",
        {
            "profile": profile,
            "student": student,
            "display_name": display_name,
            "rows": rows,
            "records": records[:50],
        },
    )


@student_required
def student_results(request):
    profile, reference, student, database_online, display_name = _student_identity(request.user)
    results = Result.objects.filter(enrollment__student_ref=reference).select_related("enrollment__course")
    return render(
        request,
        "accounts/student_results.html",
        {"profile": profile, "student": student, "display_name": display_name, "results": results},
    )


@student_required
def student_fees(request):
    profile, reference, student, database_online, display_name = _student_identity(request.user)
    fees = StudentFee.objects.filter(student_ref=reference)
    return render(
        request,
        "accounts/student_fees.html",
        {
            "profile": profile,
            "student": student,
            "display_name": display_name,
            "fees": fees,
            "total_amount": sum((item.amount for item in fees), Decimal("0")),
            "total_paid": sum((item.paid_amount for item in fees), Decimal("0")),
            "total_balance": sum((item.balance for item in fees), Decimal("0")),
        },
    )


@student_required
def student_routine(request):
    profile, reference, student, database_online, display_name = _student_identity(request.user)
    routines = ClassRoutine.objects.filter(course__enrollments__student_ref=reference).select_related("course").distinct()
    return render(
        request,
        "accounts/student_routine.html",
        {"profile": profile, "student": student, "display_name": display_name, "routines": routines},
    )


@student_required
def student_notices(request):
    profile, reference, student, database_online, display_name = _student_identity(request.user)
    notices = Notice.objects.filter(active=True, audience__in=["All", "Students"])
    return render(
        request,
        "accounts/notices.html",
        {"notices": notices, "portal_title": "Student Notices", "display_name": display_name},
    )


@student_required
def student_bus_card(request):
    profile, reference, student, database_online, display_name = _student_identity(request.user)
    academic_year = _current_academic_year()
    application = BusCardApplication.objects.filter(student_ref=reference, academic_year=academic_year).first()
    editable = application is None or application.status in {"Pending", "Rejected"}
    form = StudentBusCardForm(request.POST or None, instance=application if editable else None)

    if request.method == "POST":
        if not editable:
            messages.warning(request, "This application can no longer be edited.")
            return redirect("student_bus_card")
        if form.is_valid():
            item = form.save(commit=False)
            item.student_ref = reference
            item.student_name = display_name
            item.department = student.dept if student else ""
            item.semester = student.semester if student else 1
            item.academic_year = academic_year
            item.status = "Pending"
            item.admin_note = ""
            item.save()
            messages.success(request, "Your bus card application has been submitted.")
            return redirect("student_bus_card")

    return render(
        request,
        "accounts/student_bus_card.html",
        {
            "profile": profile,
            "student": student,
            "display_name": display_name,
            "academic_year": academic_year,
            "application": application,
            "editable": editable,
            "form": form,
        },
    )


def _teacher_assignment_or_404(request, assignment_id):
    profile = get_user_profile(request.user)
    return get_object_or_404(
        CourseAssignment.objects.select_related("course", "course__department"),
        teacher_ref=profile.reference_id,
        pk=assignment_id,
    )


@teacher_required
def teacher_portal(request):
    profile, reference, teacher, database_online, display_name = _teacher_identity(request.user)
    assignments = CourseAssignment.objects.filter(teacher_ref=reference).select_related("course", "course__department")
    assignment_filters = Q()
    for assignment in assignments:
        assignment_filters |= Q(
            course=assignment.course,
            academic_year=assignment.academic_year,
            semester=assignment.semester,
        )
    enrollments = Enrollment.objects.filter(assignment_filters) if assignments else Enrollment.objects.none()
    recent_attendance = Attendance.objects.filter(enrollment__in=enrollments).select_related(
        "enrollment", "enrollment__course"
    )[:8]
    notices = Notice.objects.filter(active=True, audience__in=["All", "Teachers"])[:5]
    mongo_online, active_book_count, recent_books = _member_library_summary(reference)
    context = {
        "profile": profile,
        "teacher": teacher,
        "database_online": database_online,
        "display_name": display_name,
        "assignments": assignments[:4],
        "assignment_count": assignments.count(),
        "student_count": enrollments.values("student_ref").distinct().count(),
        "recent_attendance": recent_attendance,
        "notices": notices,
        "mongo_online": mongo_online,
        "active_book_count": active_book_count,
        "recent_books": recent_books,
    }
    return render(request, "accounts/teacher_portal.html", context)


@teacher_required
def teacher_profile(request):
    profile, reference, teacher, database_online, display_name = _teacher_identity(request.user)
    return render(
        request,
        "accounts/teacher_profile.html",
        {
            "profile": profile,
            "teacher": teacher,
            "database_online": database_online,
            "display_name": display_name,
        },
    )


@teacher_required
def teacher_courses(request):
    profile, reference, teacher, database_online, display_name = _teacher_identity(request.user)
    assignments = CourseAssignment.objects.filter(teacher_ref=reference).select_related("course", "course__department")
    return render(
        request,
        "accounts/teacher_courses.html",
        {"profile": profile, "teacher": teacher, "display_name": display_name, "assignments": assignments},
    )


@teacher_required
def teacher_attendance_center(request):
    profile, reference, teacher, database_online, display_name = _teacher_identity(request.user)
    assignments = CourseAssignment.objects.filter(teacher_ref=reference).select_related("course", "course__department")
    return render(
        request,
        "accounts/teacher_work_center.html",
        {
            "assignments": assignments,
            "display_name": display_name,
            "title": "Take Attendance",
            "subtitle": "Choose an assigned course and attendance date.",
            "action_url_name": "teacher_attendance",
            "action_label": "Open Attendance",
        },
    )


@teacher_required
def teacher_results_center(request):
    profile, reference, teacher, database_online, display_name = _teacher_identity(request.user)
    assignments = CourseAssignment.objects.filter(teacher_ref=reference).select_related("course", "course__department")
    return render(
        request,
        "accounts/teacher_work_center.html",
        {
            "assignments": assignments,
            "display_name": display_name,
            "title": "Manage Results",
            "subtitle": "Choose a course to enter or update assessment results.",
            "action_url_name": "teacher_results",
            "action_label": "Open Results",
        },
    )


@teacher_required
def teacher_routine(request):
    profile, reference, teacher, database_online, display_name = _teacher_identity(request.user)
    assignments = CourseAssignment.objects.filter(teacher_ref=reference)
    course_ids = assignments.values_list("course_id", flat=True)
    routines = ClassRoutine.objects.filter(course_id__in=course_ids).select_related("course")
    return render(
        request,
        "accounts/teacher_routine.html",
        {"profile": profile, "teacher": teacher, "display_name": display_name, "routines": routines},
    )


@teacher_required
def teacher_notices(request):
    profile, reference, teacher, database_online, display_name = _teacher_identity(request.user)
    notices = Notice.objects.filter(active=True, audience__in=["All", "Teachers"])
    return render(
        request,
        "accounts/notices.html",
        {"notices": notices, "portal_title": "Faculty Notices", "display_name": display_name},
    )


@teacher_required
def teacher_course(request, assignment_id):
    assignment = _teacher_assignment_or_404(request, assignment_id)
    enrollments = Enrollment.objects.filter(
        course=assignment.course,
        academic_year=assignment.academic_year,
        semester=assignment.semester,
    ).select_related("course")
    results = Result.objects.filter(enrollment__in=enrollments).select_related("enrollment")
    return render(
        request,
        "accounts/teacher_course.html",
        {"assignment": assignment, "enrollments": enrollments, "results": results},
    )


@teacher_required
def teacher_attendance(request, assignment_id):
    assignment = _teacher_assignment_or_404(request, assignment_id)
    enrollments = list(
        Enrollment.objects.filter(
            course=assignment.course,
            academic_year=assignment.academic_year,
            semester=assignment.semester,
        ).order_by("student_ref")
    )
    selected_date = timezone.localdate()
    raw_date = request.POST.get("date") or request.GET.get("date")
    if raw_date:
        try:
            selected_date = date.fromisoformat(raw_date)
        except ValueError:
            messages.warning(request, "Invalid date. Today's date is being used.")

    if request.method == "POST":
        valid_statuses = {choice[0] for choice in Attendance.STATUS_CHOICES}
        for enrollment in enrollments:
            status = request.POST.get(f"status_{enrollment.pk}", Attendance.PRESENT)
            if status not in valid_statuses:
                status = Attendance.PRESENT
            remarks = request.POST.get(f"remarks_{enrollment.pk}", "").strip()
            Attendance.objects.update_or_create(
                enrollment=enrollment,
                date=selected_date,
                defaults={"status": status, "remarks": remarks},
            )
        messages.success(request, f"Attendance saved for {assignment.course.code} on {selected_date}.")
        return redirect(f"{request.path}?date={selected_date.isoformat()}")

    existing = {
        item.enrollment_id: item
        for item in Attendance.objects.filter(enrollment__in=enrollments, date=selected_date)
    }
    rows = [
        {
            "enrollment": enrollment,
            "record": existing.get(enrollment.pk),
            "status": existing.get(enrollment.pk).status if existing.get(enrollment.pk) else Attendance.PRESENT,
            "remarks": existing.get(enrollment.pk).remarks if existing.get(enrollment.pk) else "",
        }
        for enrollment in enrollments
    ]
    return render(
        request,
        "accounts/teacher_attendance.html",
        {
            "assignment": assignment,
            "rows": rows,
            "selected_date": selected_date,
            "status_choices": Attendance.STATUS_CHOICES,
        },
    )


@teacher_required
def teacher_results(request, assignment_id):
    assignment = _teacher_assignment_or_404(request, assignment_id)
    enrollments = Enrollment.objects.filter(
        course=assignment.course,
        academic_year=assignment.academic_year,
        semester=assignment.semester,
    ).order_by("student_ref")

    if request.method == "POST":
        enrollment = get_object_or_404(enrollments, pk=request.POST.get("enrollment_id"))
        exam_type = request.POST.get("exam_type", "")
        valid_exams = {choice[0] for choice in Result.EXAM_CHOICES}
        if exam_type not in valid_exams:
            messages.error(request, "Choose a valid exam type.")
            return redirect("teacher_results", assignment_id=assignment_id)
        try:
            marks = Decimal(request.POST.get("marks", ""))
        except (InvalidOperation, TypeError):
            messages.error(request, "Enter a valid mark between 0 and 100.")
            return redirect("teacher_results", assignment_id=assignment_id)
        if marks < 0 or marks > 100:
            messages.error(request, "Marks must be between 0 and 100.")
            return redirect("teacher_results", assignment_id=assignment_id)
        Result.objects.update_or_create(
            enrollment=enrollment,
            exam_type=exam_type,
            defaults={"marks": marks, "remarks": request.POST.get("remarks", "").strip()},
        )
        messages.success(request, f"Result saved for {enrollment.student_name}.")
        return redirect("teacher_results", assignment_id=assignment_id)

    results = Result.objects.filter(enrollment__in=enrollments).select_related("enrollment").order_by(
        "enrollment__student_ref", "exam_type"
    )
    return render(
        request,
        "accounts/teacher_results.html",
        {
            "assignment": assignment,
            "enrollments": enrollments,
            "results": results,
            "exam_choices": Result.EXAM_CHOICES,
        },
    )
