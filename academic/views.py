from decimal import Decimal

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AttendanceForm,
    BusCardAdminForm,
    ClassRoutineForm,
    CourseAssignmentForm,
    CourseForm,
    DepartmentForm,
    EnrollmentForm,
    NoticeForm,
    ResultForm,
    StudentFeeForm,
)
from .models import (
    Attendance,
    BusCardApplication,
    ClassRoutine,
    Course,
    CourseAssignment,
    Department,
    Enrollment,
    Notice,
    Result,
    StudentFee,
)


def academic_dashboard(request):
    fee_totals = StudentFee.objects.aggregate(total=Sum("amount"), paid=Sum("paid_amount"))
    total_fee = fee_totals["total"] or Decimal("0")
    paid_fee = fee_totals["paid"] or Decimal("0")
    context = {
        "department_count": Department.objects.count(),
        "course_count": Course.objects.filter(active=True).count(),
        "enrollment_count": Enrollment.objects.count(),
        "assignment_count": CourseAssignment.objects.count(),
        "attendance_count": Attendance.objects.count(),
        "result_count": Result.objects.count(),
        "fee_due": max(total_fee - paid_fee, Decimal("0")),
        "notice_count": Notice.objects.filter(active=True).count(),
        "pending_bus_cards": BusCardApplication.objects.filter(status="Pending").count(),
        "recent_notices": Notice.objects.filter(active=True)[:5],
        "routines": ClassRoutine.objects.select_related("course")[:8],
    }
    return render(request, "academic/dashboard.html", context)


def _list_view(
    request,
    *,
    queryset,
    title,
    subtitle,
    headers,
    row_builder,
    search_fields,
    add_url,
    edit_url,
    delete_url,
):
    query = request.GET.get("q", "").strip()
    if query:
        search_q = Q()
        for field in search_fields:
            search_q |= Q(**{f"{field}__icontains": query})
        queryset = queryset.filter(search_q)

    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    rows = [{"pk": obj.pk, "cells": row_builder(obj)} for obj in page_obj.object_list]
    return render(
        request,
        "academic/entity_list.html",
        {
            "title": title,
            "subtitle": subtitle,
            "headers": headers,
            "rows": rows,
            "page_obj": page_obj,
            "query": query,
            "add_url": add_url,
            "edit_url": edit_url,
            "delete_url": delete_url,
        },
    )


def _form_view(request, *, form_class, title, list_url, instance=None, initial=None):
    form = form_class(request.POST or None, instance=instance, initial=initial)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{title.replace('Add ', '').replace('Edit ', '')} saved successfully.")
        return redirect(list_url)
    return render(
        request,
        "academic/form.html",
        {"form": form, "title": title, "list_url": list_url, "is_edit": instance is not None},
    )


def _delete_view(request, *, model, title, list_url, pk):
    obj = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, f"{title} deleted successfully.")
        return redirect(list_url)
    return render(
        request,
        "academic/confirm_delete.html",
        {"object": obj, "title": title, "list_url": list_url},
    )


def department_list(request):
    return _list_view(
        request,
        queryset=Department.objects.all(),
        title="Departments",
        subtitle="Manage university academic departments stored in SQLite.",
        headers=["Code", "Department", "Office", "Phone"],
        row_builder=lambda x: [x.code, x.name, x.office or "—", x.phone or "—"],
        search_fields=["code", "name", "office"],
        add_url="department_add",
        edit_url="department_edit",
        delete_url="department_delete",
    )


def department_add(request):
    return _form_view(request, form_class=DepartmentForm, title="Add Department", list_url="department_list")


def department_edit(request, pk):
    return _form_view(
        request,
        form_class=DepartmentForm,
        title="Edit Department",
        list_url="department_list",
        instance=get_object_or_404(Department, pk=pk),
    )


def department_delete(request, pk):
    return _delete_view(request, model=Department, title="Department", list_url="department_list", pk=pk)


def course_list(request):
    return _list_view(
        request,
        queryset=Course.objects.select_related("department"),
        title="Courses",
        subtitle="Course catalog, credits, semesters and department ownership.",
        headers=["Code", "Title", "Department", "Semester", "Credit", "Status"],
        row_builder=lambda x: [
            x.code,
            x.title,
            x.department.code,
            x.get_semester_display(),
            x.credit,
            "Active" if x.active else "Inactive",
        ],
        search_fields=["code", "title", "department__code", "department__name"],
        add_url="course_add",
        edit_url="course_edit",
        delete_url="course_delete",
    )


def course_add(request):
    return _form_view(request, form_class=CourseForm, title="Add Course", list_url="course_list")


def course_edit(request, pk):
    return _form_view(
        request,
        form_class=CourseForm,
        title="Edit Course",
        list_url="course_list",
        instance=get_object_or_404(Course, pk=pk),
    )


def course_delete(request, pk):
    return _delete_view(request, model=Course, title="Course", list_url="course_list", pk=pk)


def enrollment_list(request):
    return _list_view(
        request,
        queryset=Enrollment.objects.select_related("course"),
        title="Enrollments",
        subtitle="Manage student course registrations and academic sessions.",
        headers=["Student ID", "Student", "Course", "Academic Year", "Semester"],
        row_builder=lambda x: [x.student_ref, x.student_name, x.course.code, x.academic_year, x.semester],
        search_fields=["student_ref", "student_name", "course__code", "course__title", "academic_year"],
        add_url="enrollment_add",
        edit_url="enrollment_edit",
        delete_url="enrollment_delete",
    )


def enrollment_add(request):
    return _form_view(request, form_class=EnrollmentForm, title="Add Enrollment", list_url="enrollment_list")


def enrollment_edit(request, pk):
    return _form_view(
        request,
        form_class=EnrollmentForm,
        title="Edit Enrollment",
        list_url="enrollment_list",
        instance=get_object_or_404(Enrollment, pk=pk),
    )


def enrollment_delete(request, pk):
    return _delete_view(request, model=Enrollment, title="Enrollment", list_url="enrollment_list", pk=pk)


def assignment_list(request):
    return _list_view(
        request,
        queryset=CourseAssignment.objects.select_related("course"),
        title="Course Assignments",
        subtitle="Assign faculty members to courses and academic sessions.",
        headers=["Teacher ID", "Teacher", "Course", "Academic Year", "Semester"],
        row_builder=lambda x: [x.teacher_ref, x.teacher_name, x.course.code, x.academic_year, x.semester],
        search_fields=["teacher_ref", "teacher_name", "course__code", "course__title", "academic_year"],
        add_url="assignment_add",
        edit_url="assignment_edit",
        delete_url="assignment_delete",
    )


def assignment_add(request):
    teacher_ref = request.GET.get("teacher_ref", "").strip()
    initial = {"teacher_ref": teacher_ref} if teacher_ref else None
    return _form_view(
        request,
        form_class=CourseAssignmentForm,
        title="Assign Course to Teacher",
        list_url="assignment_list",
        initial=initial,
    )


def assignment_edit(request, pk):
    return _form_view(
        request,
        form_class=CourseAssignmentForm,
        title="Edit Teacher Course Assignment",
        list_url="assignment_list",
        instance=get_object_or_404(CourseAssignment, pk=pk),
    )


def assignment_delete(request, pk):
    return _delete_view(request, model=CourseAssignment, title="Course assignment", list_url="assignment_list", pk=pk)


def attendance_list(request):
    return _list_view(
        request,
        queryset=Attendance.objects.select_related("enrollment", "enrollment__course"),
        title="Attendance",
        subtitle="Daily attendance records for enrolled students.",
        headers=["Date", "Student ID", "Student", "Course", "Status", "Remarks"],
        row_builder=lambda x: [
            x.date,
            x.enrollment.student_ref,
            x.enrollment.student_name,
            x.enrollment.course.code,
            x.get_status_display(),
            x.remarks or "—",
        ],
        search_fields=[
            "enrollment__student_ref",
            "enrollment__student_name",
            "enrollment__course__code",
            "status",
            "remarks",
        ],
        add_url="attendance_add",
        edit_url="attendance_edit",
        delete_url="attendance_delete",
    )


def attendance_add(request):
    return _form_view(request, form_class=AttendanceForm, title="Add Attendance", list_url="attendance_list")


def attendance_edit(request, pk):
    return _form_view(
        request,
        form_class=AttendanceForm,
        title="Edit Attendance",
        list_url="attendance_list",
        instance=get_object_or_404(Attendance, pk=pk),
    )


def attendance_delete(request, pk):
    return _delete_view(request, model=Attendance, title="Attendance", list_url="attendance_list", pk=pk)


def result_list(request):
    return _list_view(
        request,
        queryset=Result.objects.select_related("enrollment", "enrollment__course"),
        title="Results",
        subtitle="Assessment marks with automatic letter-grade calculation.",
        headers=["Student ID", "Student", "Course", "Exam", "Marks", "Grade"],
        row_builder=lambda x: [
            x.enrollment.student_ref,
            x.enrollment.student_name,
            x.enrollment.course.code,
            x.exam_type,
            x.marks,
            x.grade,
        ],
        search_fields=[
            "enrollment__student_ref",
            "enrollment__student_name",
            "enrollment__course__code",
            "exam_type",
            "grade",
        ],
        add_url="result_add",
        edit_url="result_edit",
        delete_url="result_delete",
    )


def result_add(request):
    return _form_view(request, form_class=ResultForm, title="Add Result", list_url="result_list")


def result_edit(request, pk):
    return _form_view(
        request,
        form_class=ResultForm,
        title="Edit Result",
        list_url="result_list",
        instance=get_object_or_404(Result, pk=pk),
    )


def result_delete(request, pk):
    return _delete_view(request, model=Result, title="Result", list_url="result_list", pk=pk)


def fee_list(request):
    return _list_view(
        request,
        queryset=StudentFee.objects.all(),
        title="Student Fees",
        subtitle="Track payable, paid and outstanding student fees.",
        headers=["Student ID", "Student", "Fee Type", "Amount", "Paid", "Balance", "Due Date", "Status"],
        row_builder=lambda x: [
            x.student_ref,
            x.student_name,
            x.fee_type,
            x.amount,
            x.paid_amount,
            x.balance,
            x.due_date,
            x.status,
        ],
        search_fields=["student_ref", "student_name", "fee_type", "status", "reference"],
        add_url="fee_add",
        edit_url="fee_edit",
        delete_url="fee_delete",
    )


def fee_add(request):
    return _form_view(request, form_class=StudentFeeForm, title="Add Student Fee", list_url="fee_list")


def fee_edit(request, pk):
    return _form_view(
        request,
        form_class=StudentFeeForm,
        title="Edit Student Fee",
        list_url="fee_list",
        instance=get_object_or_404(StudentFee, pk=pk),
    )


def fee_delete(request, pk):
    return _delete_view(request, model=StudentFee, title="Student fee", list_url="fee_list", pk=pk)


def routine_list(request):
    return _list_view(
        request,
        queryset=ClassRoutine.objects.select_related("course"),
        title="Class Routine",
        subtitle="Weekly class schedule with room and teacher information.",
        headers=["Day", "Start", "End", "Course", "Room", "Teacher"],
        row_builder=lambda x: [x.day, x.start_time, x.end_time, x.course.code, x.room, x.teacher_name or "—"],
        search_fields=["day", "course__code", "course__title", "room", "teacher_name"],
        add_url="routine_add",
        edit_url="routine_edit",
        delete_url="routine_delete",
    )


def routine_add(request):
    return _form_view(request, form_class=ClassRoutineForm, title="Add Routine", list_url="routine_list")


def routine_edit(request, pk):
    return _form_view(
        request,
        form_class=ClassRoutineForm,
        title="Edit Routine",
        list_url="routine_list",
        instance=get_object_or_404(ClassRoutine, pk=pk),
    )


def routine_delete(request, pk):
    return _delete_view(request, model=ClassRoutine, title="Routine entry", list_url="routine_list", pk=pk)


def notice_list(request):
    return _list_view(
        request,
        queryset=Notice.objects.all(),
        title="Notices",
        subtitle="Publish announcements for students, teachers, staff, or everyone.",
        headers=["Publish Date", "Title", "Audience", "Status"],
        row_builder=lambda x: [x.publish_date, x.title, x.get_audience_display(), "Active" if x.active else "Inactive"],
        search_fields=["title", "content", "audience"],
        add_url="notice_add",
        edit_url="notice_edit",
        delete_url="notice_delete",
    )


def notice_add(request):
    return _form_view(request, form_class=NoticeForm, title="Add Notice", list_url="notice_list")


def notice_edit(request, pk):
    return _form_view(
        request,
        form_class=NoticeForm,
        title="Edit Notice",
        list_url="notice_list",
        instance=get_object_or_404(Notice, pk=pk),
    )


def notice_delete(request, pk):
    return _delete_view(request, model=Notice, title="Notice", list_url="notice_list", pk=pk)


def bus_card_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    applications = BusCardApplication.objects.all()
    if query:
        applications = applications.filter(
            Q(student_ref__icontains=query)
            | Q(student_name__icontains=query)
            | Q(department__icontains=query)
            | Q(pickup_point__icontains=query)
            | Q(card_number__icontains=query)
        )
    if status:
        applications = applications.filter(status=status)
    paginator = Paginator(applications, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "academic/bus_card_list.html",
        {
            "page_obj": page_obj,
            "applications": page_obj.object_list,
            "query": query,
            "selected_status": status,
            "status_choices": BusCardApplication.STATUS_CHOICES,
        },
    )


def bus_card_review(request, pk):
    application = get_object_or_404(BusCardApplication, pk=pk)
    form = BusCardAdminForm(request.POST or None, instance=application)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Bus card application for {application.student_name} was updated.")
        return redirect("bus_card_list")
    return render(
        request,
        "academic/bus_card_review.html",
        {"application": application, "form": form},
    )
