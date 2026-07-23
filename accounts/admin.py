from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "reference_id", "display_name", "updated_at")
    list_filter = ("role",)
    search_fields = ("user__username", "reference_id", "display_name")
