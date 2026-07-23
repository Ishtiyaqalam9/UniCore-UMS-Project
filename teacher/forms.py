from django import forms

from .models import Teacher


class DateInput(forms.DateInput):
    input_type = "date"


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            "employee_id",
            "name",
            "age",
            "department",
            "designation",
            "subject",
            "email",
            "phone",
            "joining_date",
            "status",
            "address",
        ]
        widgets = {
            "joining_date": DateInput(),
            "address": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "employee_id": "Leave blank to generate automatically, for example TCH-0001.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            if field.required:
                field.widget.attrs["required"] = True
