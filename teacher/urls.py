from django.urls import path

from accounts.decorators import admin_required
from . import views

urlpatterns = [
    path("", admin_required(views.teacher_list), name="teacher_list"),
    path("add/", admin_required(views.add_teacher), name="add_teacher"),
    path("<int:pk>/edit/", admin_required(views.edit_teacher), name="edit_teacher"),
    path("<int:pk>/delete/", admin_required(views.delete_teacher), name="delete_teacher"),
]
