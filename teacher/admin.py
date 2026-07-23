from django.contrib import admin

from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "name", "department", "designation", "subject", "email", "phone", "status")
    list_filter = ("department", "designation", "status")
    search_fields = ("employee_id", "name", "subject", "email", "phone")
