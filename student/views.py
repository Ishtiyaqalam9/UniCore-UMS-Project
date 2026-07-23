from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentForm
from .models import Student


def student_list(request):
    students = Student.objects.all()
    query = request.GET.get("q", "").strip()
    department = request.GET.get("department", "").strip()
    status = request.GET.get("status", "").strip()

    if query:
        students = students.filter(
            Q(student_id__icontains=query)
            | Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
        )
    if department:
        students = students.filter(dept__iexact=department)
    if status:
        students = students.filter(status=status)

    departments = (
        Student.objects.exclude(dept="")
        .values_list("dept", flat=True)
        .distinct()
        .order_by("dept")
    )
    page_obj = Paginator(students, 20).get_page(request.GET.get("page"))
    return render(
        request,
        "student/student_list.html",
        {
            "page_obj": page_obj,
            "students": page_obj.object_list,
            "departments": departments,
            "query": query,
            "selected_department": department,
            "selected_status": status,
            "status_choices": Student.STATUS_CHOICES,
        },
    )


def add_student(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student added successfully to the MySQL database.")
        return redirect("student_list")
    return render(request, "student/student_form.html", {"form": form, "title": "Add Student"})


def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student updated successfully.")
        return redirect("student_list")
    return render(
        request,
        "student/student_form.html",
        {"form": form, "title": "Edit Student", "student": student},
    )


def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully.")
        return redirect("student_list")
    return render(
        request,
        "student/student_confirm_delete.html",
        {"student": student},
    )
