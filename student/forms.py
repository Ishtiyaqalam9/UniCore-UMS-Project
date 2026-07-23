from django import forms

from .models import Student


class DateInput(forms.DateInput):
    input_type = "date"


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "student_id",
            "name",
            "age",
            "gender",
            "dept",
            "semester",
            "email",
            "phone",
            "admission_date",
            "status",
            "address",
        ]
        widgets = {
            "admission_date": DateInput(),
            "address": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "student_id": "Leave blank to generate automatically, for example STU-0001.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            if field.required:
                field.widget.attrs["required"] = True
