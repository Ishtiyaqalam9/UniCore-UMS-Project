from datetime import date
from decimal import Decimal

from django.test import TestCase

from .models import Course, Department, Enrollment, Result, StudentFee


class AcademicModelTests(TestCase):
    databases = {"default"}

    def setUp(self):
        self.department = Department.objects.create(code="CSE", name="Computer Science and Engineering")
        self.course = Course.objects.create(code="CSE-101", title="Introduction to Computing", department=self.department)
        self.enrollment = Enrollment.objects.create(
            student_ref="STU-0001",
            student_name="Demo Student",
            course=self.course,
            academic_year="2026-2027",
            semester=1,
        )

    def test_result_grade_is_calculated(self):
        result = Result.objects.create(enrollment=self.enrollment, exam_type="Final", marks=Decimal("82"))
        self.assertEqual(result.grade, "A+")

    def test_fee_status_and_balance(self):
        fee = StudentFee.objects.create(
            student_ref="STU-0001",
            student_name="Demo Student",
            fee_type="Tuition",
            amount=Decimal("10000"),
            paid_amount=Decimal("4000"),
            due_date=date.today(),
        )
        self.assertEqual(fee.status, "Partial")
        self.assertEqual(fee.balance, Decimal("6000"))
