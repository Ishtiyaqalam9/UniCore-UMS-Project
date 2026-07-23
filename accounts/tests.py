from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from academic.models import Attendance, BusCardApplication, Course, CourseAssignment, Department, Enrollment, Result, StudentFee
from student.models import Student
from teacher.models import Teacher

from .models import UserProfile


class RolePortalTests(TestCase):
    databases = {"default", "mysql", "postgres"}

    def setUp(self):
        Student.objects.using("mysql").create(
            student_id="STU-0001", name="Student One", age=20, dept="CSE", semester=1,
            email="student@example.com", phone="01700000000", status="Active",
        )
        Teacher.objects.using("postgres").create(
            employee_id="TCH-0001", name="Teacher One", age=35, subject="Database Systems",
            department="CSE", designation="Lecturer", email="teacher@example.com",
            phone="01800000000", status="Active",
        )
        self.department = Department.objects.create(code="CSE", name="Computer Science")
        self.course = Course.objects.create(code="CSE101", title="Database Systems", department=self.department)
        self.enrollment = Enrollment.objects.create(
            student_ref="STU-0001",
            student_name="Student One",
            course=self.course,
            academic_year="2026-2027",
            semester=1,
        )
        self.other_course = Course.objects.create(code="CSE202", title="Other Course", department=self.department)
        self.other_enrollment = Enrollment.objects.create(
            student_ref="STU-9999", student_name="Other Student", course=self.other_course,
            academic_year="2026-2027", semester=1,
        )
        self.other_assignment = CourseAssignment.objects.create(
            teacher_ref="TCH-9999", teacher_name="Other Teacher", course=self.other_course,
            academic_year="2026-2027", semester=1,
        )
        self.assignment = CourseAssignment.objects.create(
            teacher_ref="TCH-0001",
            teacher_name="Teacher One",
            course=self.course,
            academic_year="2026-2027",
            semester=1,
        )

        self.student_user = User.objects.create_user("student1", password="Testpass123!")
        UserProfile.objects.create(
            user=self.student_user,
            role=UserProfile.STUDENT,
            reference_id="STU-0001",
            display_name="Student One",
        )
        self.teacher_user = User.objects.create_user("teacher1", password="Testpass123!")
        UserProfile.objects.create(
            user=self.teacher_user,
            role=UserProfile.TEACHER,
            reference_id="TCH-0001",
            display_name="Teacher One",
        )
        self.admin_user = User.objects.create_superuser("admin", "admin@example.com", "Testpass123!")

    def test_student_can_open_own_portal_but_not_admin_student_list(self):
        self.client.force_login(self.student_user)
        portal = self.client.get(reverse("student_portal"))
        self.assertEqual(portal.status_code, 200)
        self.assertContains(portal, "Student One")
        self.assertContains(portal, "CSE101")
        self.assertNotContains(portal, "CSE202")
        response = self.client.get(reverse("student_list"))
        self.assertRedirects(response, reverse("student_portal"))

    def test_teacher_can_mark_only_assigned_course_attendance(self):
        self.client.force_login(self.teacher_user)
        response = self.client.post(
            reverse("teacher_attendance", args=[self.assignment.id]),
            {
                "date": date.today().isoformat(),
                f"status_{self.enrollment.id}": Attendance.PRESENT,
                f"remarks_{self.enrollment.id}": "On time",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Attendance.objects.filter(enrollment=self.enrollment).exists())
        page = self.client.get(reverse("teacher_attendance", args=[self.assignment.id]))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Student One")

    def test_teacher_can_create_result_for_assigned_course(self):
        self.client.force_login(self.teacher_user)
        response = self.client.post(
            reverse("teacher_results", args=[self.assignment.id]),
            {
                "enrollment_id": self.enrollment.id,
                "exam_type": "Final",
                "marks": "82",
                "remarks": "Good",
            },
        )
        self.assertEqual(response.status_code, 302)
        result = Result.objects.get(enrollment=self.enrollment, exam_type="Final")
        self.assertEqual(result.grade, "A+")
        page = self.client.get(reverse("teacher_results", args=[self.assignment.id]))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "A+")


    def test_teacher_cannot_open_another_teachers_assignment(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse("teacher_course", args=[self.other_assignment.id]))
        self.assertEqual(response.status_code, 404)


    @patch("accounts.views.is_available", return_value=False)
    def test_student_navigation_pages_render(self, mocked_library):
        self.client.force_login(self.student_user)
        pages = [
            "student_portal", "student_profile", "student_courses",
            "student_course_registration", "student_attendance_summary",
            "student_results", "student_fees", "student_routine",
            "student_notices", "student_bus_card",
        ]
        for name in pages:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_student_can_register_available_course(self):
        self.client.force_login(self.student_user)
        response = self.client.post(
            reverse("student_course_registration"),
            {"course_id": self.other_course.id},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Enrollment.objects.filter(student_ref="STU-0001", course=self.other_course).exists()
        )

    def test_student_can_submit_bus_card_application(self):
        self.client.force_login(self.student_user)
        response = self.client.post(
            reverse("student_bus_card"),
            {
                "phone": "01700000000",
                "pickup_point": "Mirpur 10",
                "address": "Dhaka",
                "emergency_contact": "01800000000",
                "blood_group": "A+",
            },
        )
        self.assertEqual(response.status_code, 302)
        item = BusCardApplication.objects.get(student_ref="STU-0001")
        self.assertEqual(item.status, "Pending")
        self.assertEqual(item.student_name, "Student One")

    @patch("accounts.views.is_available", return_value=False)
    def test_teacher_navigation_pages_render(self, mocked_library):
        self.client.force_login(self.teacher_user)
        pages = [
            "teacher_portal", "teacher_profile", "teacher_courses",
            "teacher_attendance_center", "teacher_results_center",
            "teacher_routine", "teacher_notices",
        ]
        for name in pages:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    @patch("library.views.is_available", return_value=False)
    def test_student_and_teacher_can_open_library_catalog(self, mocked_library):
        for user in [self.student_user, self.teacher_user]:
            self.client.force_login(user)
            self.assertEqual(self.client.get(reverse("member_library_catalog")).status_code, 200)
            self.assertEqual(self.client.get(reverse("my_library")).status_code, 200)

    @patch("library.views.is_available", return_value=False)
    def test_admin_management_pages_render(self, mocked_library):
        self.client.force_login(self.admin_user)
        for name in [
            "home", "student_list", "teacher_list", "academic_dashboard",
            "bus_card_list", "account_list", "library_list", "issue_list",
        ]:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

        application = BusCardApplication.objects.create(
            student_ref="STU-0001", student_name="Student One", department="CSE",
            semester=1, academic_year="2026-2027", phone="01700000000",
            pickup_point="Mirpur 10", address="Dhaka", emergency_contact="01800000000",
        )
        self.assertEqual(
            self.client.get(reverse("bus_card_review", args=[application.id])).status_code,
            200,
        )
