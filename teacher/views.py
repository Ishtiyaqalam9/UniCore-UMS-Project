from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TeacherForm
from .models import Teacher


def teacher_list(request):
    teachers = Teacher.objects.all()
    query = request.GET.get("q", "").strip()
    department = request.GET.get("department", "").strip()
    status = request.GET.get("status", "").strip()

    if query:
        teachers = teachers.filter(
            Q(employee_id__icontains=query)
            | Q(name__icontains=query)
            | Q(subject__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
        )
    if department:
        teachers = teachers.filter(department__iexact=department)
    if status:
        teachers = teachers.filter(status=status)

    departments = (
        Teacher.objects.exclude(department="")
        .values_list("department", flat=True)
        .distinct()
        .order_by("department")
    )
    page_obj = Paginator(teachers, 20).get_page(request.GET.get("page"))
    return render(
        request,
        "teacher/teacher_list.html",
        {
            "page_obj": page_obj,
            "teachers": page_obj.object_list,
            "departments": departments,
            "query": query,
            "selected_department": department,
            "selected_status": status,
            "status_choices": Teacher.STATUS_CHOICES,
        },
    )


def add_teacher(request):
    form = TeacherForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Teacher added successfully to the PostgreSQL database.")
        return redirect("teacher_list")
    return render(request, "teacher/teacher_form.html", {"form": form, "title": "Add Teacher"})


def edit_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    form = TeacherForm(request.POST or None, instance=teacher)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Teacher updated successfully.")
        return redirect("teacher_list")
    return render(
        request,
        "teacher/teacher_form.html",
        {"form": form, "title": "Edit Teacher", "teacher": teacher},
    )


def delete_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        teacher.delete()
        messages.success(request, "Teacher deleted successfully.")
        return redirect("teacher_list")
    return render(request, "teacher/teacher_confirm_delete.html", {"teacher": teacher})
