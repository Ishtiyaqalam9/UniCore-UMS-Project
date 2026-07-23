from datetime import date, timedelta

from django import forms

from student.models import Student
from teacher.models import Teacher


class DateInput(forms.DateInput):
    input_type = "date"


class StyledForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class BookForm(StyledForm):
    book_id = forms.CharField(max_length=30, label="Book ID")
    book_name = forms.CharField(max_length=180, label="Book Name")
    writer = forms.CharField(max_length=150)
    isbn = forms.CharField(max_length=30, required=False, label="ISBN")
    category = forms.CharField(max_length=80, required=False)
    total_copies = forms.IntegerField(min_value=1, initial=1)


class IssueBookForm(StyledForm):
    BORROWER_CHOICES = [("Student", "Student"), ("Teacher", "Teacher")]

    borrower_type = forms.ChoiceField(choices=BORROWER_CHOICES)
    borrower_ref = forms.CharField(max_length=30, label="Student/Teacher ID")
    borrower_name = forms.CharField(max_length=120, required=False)
    due_date = forms.DateField(widget=DateInput(), initial=lambda: date.today() + timedelta(days=14))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def clean(self):
        cleaned = super().clean()
        borrower_type = cleaned.get("borrower_type")
        reference = (cleaned.get("borrower_ref") or "").strip()
        if not reference:
            return cleaned
        try:
            if borrower_type == "Student":
                person = Student.objects.filter(student_id=reference).first()
                if person is None and reference.isdigit():
                    person = Student.objects.filter(pk=int(reference)).first()
            else:
                person = Teacher.objects.filter(employee_id=reference).first()
                if person is None and reference.isdigit():
                    person = Teacher.objects.filter(pk=int(reference)).first()
        except Exception:
            person = None
        if person:
            cleaned["borrower_ref"] = person.reference_code
            cleaned["borrower_name"] = person.name
        elif not cleaned.get("borrower_name"):
            self.add_error("borrower_name", "Enter the borrower name when the profile service is unavailable.")
        return cleaned
