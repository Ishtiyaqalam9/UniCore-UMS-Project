from django.urls import path

from . import views

urlpatterns = [
    path("redirect/", views.portal_redirect, name="portal_redirect"),
    path("accounts/", views.account_list, name="account_list"),
    path("accounts/create/", views.account_create, name="account_create"),
    path("accounts/<int:user_id>/password/", views.account_password_reset, name="account_password_reset"),
    path("accounts/<int:user_id>/toggle/", views.account_toggle, name="account_toggle"),
    path("accounts/<int:user_id>/delete/", views.account_delete, name="account_delete"),
    path("change-password/", views.change_password, name="change_password"),

    path("student-portal/", views.student_portal, name="student_portal"),
    path("student-portal/profile/", views.student_profile, name="student_profile"),
    path("student-portal/courses/", views.student_courses, name="student_courses"),
    path("student-portal/course-registration/", views.student_course_registration, name="student_course_registration"),
    path("student-portal/courses/<int:enrollment_id>/drop/", views.student_drop_course, name="student_drop_course"),
    path("student-portal/attendance/", views.student_attendance_summary, name="student_attendance_summary"),
    path("student-portal/results/", views.student_results, name="student_results"),
    path("student-portal/fees/", views.student_fees, name="student_fees"),
    path("student-portal/routine/", views.student_routine, name="student_routine"),
    path("student-portal/notices/", views.student_notices, name="student_notices"),
    path("student-portal/bus-card/", views.student_bus_card, name="student_bus_card"),

    path("teacher-portal/", views.teacher_portal, name="teacher_portal"),
    path("teacher-portal/profile/", views.teacher_profile, name="teacher_profile"),
    path("teacher-portal/courses/", views.teacher_courses, name="teacher_courses"),
    path("teacher-portal/attendance/", views.teacher_attendance_center, name="teacher_attendance_center"),
    path("teacher-portal/results/", views.teacher_results_center, name="teacher_results_center"),
    path("teacher-portal/routine/", views.teacher_routine, name="teacher_routine"),
    path("teacher-portal/notices/", views.teacher_notices, name="teacher_notices"),
    path("teacher-portal/assignment/<int:assignment_id>/", views.teacher_course, name="teacher_course"),
    path("teacher-portal/assignment/<int:assignment_id>/attendance/", views.teacher_attendance, name="teacher_attendance"),
    path("teacher-portal/assignment/<int:assignment_id>/results/", views.teacher_results, name="teacher_results"),
]
