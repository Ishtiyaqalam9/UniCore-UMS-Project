from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from student.models import Student
from teacher.models import Teacher

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


class DateInput(forms.DateInput):
    input_type = "date"


class TimeInput(forms.TimeInput):
    input_type = "time"


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            current = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"form-control {current}".strip()


class DepartmentForm(StyledModelForm):
    class Meta:
        model = Department
        fields = ["code", "name", "office", "phone", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class CourseForm(StyledModelForm):
    class Meta:
        model = Course
        fields = ["code", "title", "credit", "department", "semester", "active"]


class StudentLookupMixin:
    student_field_name = "student_ref"

    def _configure_student_field(self):
        field_name = self.student_field_name
        try:
            students = list(Student.objects.all().order_by("name"))
        except Exception:
            students = []

        if students:
            choices = [(student.reference_code, f"{student.reference_code} — {student.name}") for student in students]
            self.fields[field_name] = forms.ChoiceField(choices=choices, label="Student")
            self.fields[field_name].widget.attrs["class"] = "form-control"
        else:
            self.fields[field_name].help_text = "MySQL is unavailable; enter an existing student ID manually."

    def clean(self):
        cleaned = super().clean()
        student_ref = cleaned.get(self.student_field_name)
        if student_ref:
            try:
                student = Student.objects.filter(student_id=student_ref).first()
                if student is None and str(student_ref).isdigit():
                    student = Student.objects.filter(pk=int(student_ref)).first()
                if student:
                    cleaned["student_name"] = student.name
            except Exception:
                pass
        return cleaned


class TeacherLookupMixin:
    teacher_field_name = "teacher_ref"

    def _configure_teacher_field(self):
        field_name = self.teacher_field_name
        try:
            teachers = list(Teacher.objects.all().order_by("name"))
        except Exception:
            teachers = []

        if teachers:
            choices = [(teacher.reference_code, f"{teacher.reference_code} — {teacher.name}") for teacher in teachers]
            self.fields[field_name] = forms.ChoiceField(choices=choices, label="Teacher")
            self.fields[field_name].widget.attrs["class"] = "form-control"
        else:
            self.fields[field_name].help_text = "PostgreSQL is unavailable; enter an existing teacher ID manually."

    def clean(self):
        cleaned = super().clean()
        teacher_ref = cleaned.get(self.teacher_field_name)
        if teacher_ref:
            try:
                teacher = Teacher.objects.filter(employee_id=teacher_ref).first()
                if teacher is None and str(teacher_ref).isdigit():
                    teacher = Teacher.objects.filter(pk=int(teacher_ref)).first()
                if teacher:
                    cleaned["teacher_name"] = teacher.name
            except Exception:
                pass
        return cleaned


class EnrollmentForm(StudentLookupMixin, StyledModelForm):
    class Meta:
        model = Enrollment
        fields = ["student_ref", "student_name", "course", "academic_year", "semester"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_student_field()
        self.fields["student_name"].help_text = "Filled automatically when the MySQL student record is available."


class CourseAssignmentForm(TeacherLookupMixin, StyledModelForm):
    class Meta:
        model = CourseAssignment
        fields = ["teacher_ref", "course", "academic_year"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_teacher_field()
        self.fields["teacher_ref"].help_text = "Select the faculty member who will manage this course."
        self.fields["course"].queryset = Course.objects.filter(active=True).select_related("department")
        self.fields["course"].help_text = "The course semester is assigned automatically."
        self.fields["academic_year"].help_text = "Example: 2026-2027"
        if not self.is_bound and not self.instance.pk:
            today = timezone.localdate()
            start_year = today.year if today.month >= 7 else today.year - 1
            self.initial.setdefault("academic_year", f"{start_year}-{start_year + 1}")

    def clean(self):
        cleaned = super().clean()
        teacher_ref = cleaned.get("teacher_ref")
        course = cleaned.get("course")
        teacher = None
        lookup_failed = False

        if teacher_ref:
            try:
                teacher = Teacher.objects.filter(employee_id=teacher_ref).first()
                if teacher is None and str(teacher_ref).isdigit():
                    teacher = Teacher.objects.filter(pk=int(teacher_ref)).first()
            except Exception:
                lookup_failed = True

            if teacher:
                cleaned["teacher_ref"] = teacher.reference_code
                self.instance.teacher_name = teacher.name
            elif lookup_failed:
                self.instance.teacher_name = self.instance.teacher_name or str(teacher_ref)
            else:
                self.add_error("teacher_ref", "Select an existing teacher record.")

        if course:
            self.instance.semester = course.semester

        normalized_ref = cleaned.get("teacher_ref")
        academic_year = cleaned.get("academic_year")
        if normalized_ref and course and academic_year:
            duplicate = CourseAssignment.objects.filter(
                teacher_ref=normalized_ref,
                course=course,
                academic_year=academic_year,
                semester=course.semester,
            )
            if self.instance.pk:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                self.add_error("course", "This course is already assigned to the selected teacher for this academic year.")

        return cleaned


class AttendanceForm(StyledModelForm):
    class Meta:
        model = Attendance
        fields = ["enrollment", "date", "status", "remarks"]
        widgets = {"date": DateInput()}


class ResultForm(StyledModelForm):
    class Meta:
        model = Result
        fields = ["enrollment", "exam_type", "marks", "remarks"]


class StudentFeeForm(StudentLookupMixin, StyledModelForm):
    class Meta:
        model = StudentFee
        fields = [
            "student_ref",
            "student_name",
            "fee_type",
            "amount",
            "paid_amount",
            "due_date",
            "reference",
        ]
        widgets = {"due_date": DateInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_student_field()

    def clean(self):
        cleaned = super().clean()
        amount = cleaned.get("amount")
        paid = cleaned.get("paid_amount")
        if amount is not None and paid is not None and paid > amount:
            raise ValidationError("Paid amount cannot be greater than the total amount.")
        return cleaned


class ClassRoutineForm(StyledModelForm):
    class Meta:
        model = ClassRoutine
        fields = ["course", "day", "start_time", "end_time", "room", "teacher_name"]
        widgets = {"start_time": TimeInput(), "end_time": TimeInput()}

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        if start and end and start >= end:
            raise ValidationError("End time must be later than start time.")
        return cleaned


class NoticeForm(StyledModelForm):
    class Meta:
        model = Notice
        fields = ["title", "audience", "content", "publish_date", "active"]
        widgets = {"content": forms.Textarea(attrs={"rows": 5}), "publish_date": DateInput()}


class BusCardAdminForm(StyledModelForm):
    class Meta:
        model = BusCardApplication
        fields = [
            "status",
            "card_number",
            "issue_date",
            "expiry_date",
            "admin_note",
        ]
        widgets = {
            "issue_date": DateInput(),
            "expiry_date": DateInput(),
            "admin_note": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned = super().clean()
        issue_date = cleaned.get("issue_date")
        expiry_date = cleaned.get("expiry_date")
        if issue_date and expiry_date and expiry_date <= issue_date:
            raise ValidationError("Expiry date must be later than the issue date.")
        return cleaned
