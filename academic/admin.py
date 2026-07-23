from django.contrib import admin

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


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "office", "phone")
    search_fields = ("code", "name")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "department", "semester", "credit", "active")
    list_filter = ("department", "semester", "active")
    search_fields = ("code", "title")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student_ref", "student_name", "course", "academic_year", "semester")
    list_filter = ("academic_year", "semester", "course")
    search_fields = ("student_ref", "student_name", "course__code")


@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher_ref", "teacher_name", "course", "academic_year", "semester")
    search_fields = ("teacher_ref", "teacher_name", "course__code")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "date", "status")
    list_filter = ("status", "date")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "exam_type", "marks", "grade")
    list_filter = ("exam_type", "grade")


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ("student_ref", "student_name", "fee_type", "amount", "paid_amount", "status", "due_date")
    list_filter = ("status", "fee_type")
    search_fields = ("student_ref", "student_name")


@admin.register(ClassRoutine)
class ClassRoutineAdmin(admin.ModelAdmin):
    list_display = ("course", "day", "start_time", "end_time", "room", "teacher_name")
    list_filter = ("day", "course")


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "publish_date", "active")
    list_filter = ("audience", "active")
    search_fields = ("title", "content")


@admin.register(BusCardApplication)
class BusCardApplicationAdmin(admin.ModelAdmin):
    list_display = ("student_ref", "student_name", "academic_year", "pickup_point", "status", "card_number")
    list_filter = ("status", "academic_year", "department")
    search_fields = ("student_ref", "student_name", "phone", "pickup_point", "card_number")
