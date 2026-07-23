from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Department(TimeStampedModel):
    code = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=120, unique=True)
    office = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Course(TimeStampedModel):
    SEMESTER_CHOICES = [(number, f"Semester {number}") for number in range(1, 13)]

    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=150)
    credit = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal("3.0"),
        validators=[MinValueValidator(Decimal("0.5")), MaxValueValidator(Decimal("12.0"))],
    )
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="courses")
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES, default=1)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["department__code", "semester", "code"]

    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(TimeStampedModel):
    student_ref = models.CharField(max_length=30, help_text="Student ID from the MySQL student database")
    student_name = models.CharField(max_length=120)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    academic_year = models.CharField(max_length=9, default="2026-2027")
    semester = models.PositiveSmallIntegerField(choices=Course.SEMESTER_CHOICES, default=1)
    enrolled_on = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-academic_year", "student_ref", "course__code"]
        constraints = [
            models.UniqueConstraint(
                fields=["student_ref", "course", "academic_year", "semester"],
                name="unique_student_course_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.student_ref} - {self.course.code}"


class CourseAssignment(TimeStampedModel):
    teacher_ref = models.CharField(max_length=30, help_text="Teacher ID from the PostgreSQL teacher database")
    teacher_name = models.CharField(max_length=120)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    academic_year = models.CharField(max_length=9, default="2026-2027")
    semester = models.PositiveSmallIntegerField(choices=Course.SEMESTER_CHOICES, default=1)

    class Meta:
        ordering = ["-academic_year", "teacher_ref", "course__code"]
        constraints = [
            models.UniqueConstraint(
                fields=["teacher_ref", "course", "academic_year", "semester"],
                name="unique_teacher_course_assignment",
            )
        ]

    def __str__(self):
        return f"{self.teacher_name} - {self.course.code}"


class Attendance(TimeStampedModel):
    PRESENT = "P"
    ABSENT = "A"
    LATE = "L"
    STATUS_CHOICES = [(PRESENT, "Present"), (ABSENT, "Absent"), (LATE, "Late")]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PRESENT)
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-date", "enrollment__student_ref"]
        constraints = [
            models.UniqueConstraint(fields=["enrollment", "date"], name="unique_daily_attendance")
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.date} - {self.get_status_display()}"


class Result(TimeStampedModel):
    EXAM_CHOICES = [
        ("Quiz", "Quiz"),
        ("Assignment", "Assignment"),
        ("Midterm", "Midterm"),
        ("Final", "Final"),
        ("Other", "Other"),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="results")
    exam_type = models.CharField(max_length=20, choices=EXAM_CHOICES)
    marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    grade = models.CharField(max_length=3, blank=True)
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["enrollment__student_ref", "enrollment__course__code", "exam_type"]
        constraints = [
            models.UniqueConstraint(fields=["enrollment", "exam_type"], name="unique_exam_result")
        ]

    def save(self, *args, **kwargs):
        score = float(self.marks)
        if score >= 80:
            self.grade = "A+"
        elif score >= 75:
            self.grade = "A"
        elif score >= 70:
            self.grade = "A-"
        elif score >= 65:
            self.grade = "B+"
        elif score >= 60:
            self.grade = "B"
        elif score >= 55:
            self.grade = "B-"
        elif score >= 50:
            self.grade = "C+"
        elif score >= 45:
            self.grade = "C"
        elif score >= 40:
            self.grade = "D"
        else:
            self.grade = "F"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enrollment} - {self.exam_type}: {self.grade}"


class StudentFee(TimeStampedModel):
    STATUS_CHOICES = [("Unpaid", "Unpaid"), ("Partial", "Partial"), ("Paid", "Paid")]

    student_ref = models.CharField(max_length=30)
    student_name = models.CharField(max_length=120)
    fee_type = models.CharField(max_length=80)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Unpaid")
    reference = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["status", "due_date", "student_ref"]

    @property
    def balance(self):
        return max(self.amount - self.paid_amount, Decimal("0"))

    def save(self, *args, **kwargs):
        if self.paid_amount <= 0:
            self.status = "Unpaid"
        elif self.paid_amount >= self.amount:
            self.status = "Paid"
        else:
            self.status = "Partial"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_ref} - {self.fee_type}"


class ClassRoutine(TimeStampedModel):
    DAY_CHOICES = [
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="routine_entries")
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=30)
    teacher_name = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["day", "start_time", "course__code"]
        constraints = [
            models.UniqueConstraint(fields=["course", "day", "start_time"], name="unique_course_routine_slot")
        ]

    def __str__(self):
        return f"{self.course.code} - {self.day} {self.start_time}"


class Notice(TimeStampedModel):
    AUDIENCE_CHOICES = [
        ("All", "Everyone"),
        ("Students", "Students"),
        ("Teachers", "Teachers"),
        ("Staff", "Staff"),
    ]

    title = models.CharField(max_length=180)
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default="All")
    content = models.TextField()
    publish_date = models.DateField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-publish_date", "-created_at"]

    def __str__(self):
        return self.title


class BusCardApplication(TimeStampedModel):
    STATUS_CHOICES = [
        ("Pending", "Pending Review"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Printed", "Card Printed"),
        ("Collected", "Collected"),
    ]
    BLOOD_GROUP_CHOICES = [
        ("", "Select blood group"),
        ("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-"),
    ]

    student_ref = models.CharField(max_length=30)
    student_name = models.CharField(max_length=120)
    department = models.CharField(max_length=120, blank=True)
    semester = models.PositiveSmallIntegerField(default=1)
    academic_year = models.CharField(max_length=9, default="2026-2027")
    phone = models.CharField(max_length=20)
    pickup_point = models.CharField(max_length=150)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=20)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="Pending")
    card_number = models.CharField(max_length=30, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    admin_note = models.TextField(blank=True)

    class Meta:
        ordering = ["status", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student_ref", "academic_year"],
                name="unique_bus_card_application_per_year",
            )
        ]

    def __str__(self):
        return f"{self.student_ref} - {self.academic_year} - {self.status}"
