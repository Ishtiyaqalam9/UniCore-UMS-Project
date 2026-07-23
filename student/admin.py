from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "name", "dept", "semester", "email", "phone", "status")
    list_filter = ("dept", "semester", "status", "gender")
    search_fields = ("student_id", "name", "email", "phone")
