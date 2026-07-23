from django.urls import path

from accounts.decorators import admin_required
from . import views

urlpatterns = [
    path("", admin_required(views.student_list), name="student_list"),
    path("add/", admin_required(views.add_student), name="add_student"),
    path("<int:pk>/edit/", admin_required(views.edit_student), name="edit_student"),
    path("<int:pk>/delete/", admin_required(views.delete_student), name="delete_student"),
]
