from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from student.models import Student
from teacher.models import Teacher
from academic.models import BusCardApplication

from .models import UserProfile
from .utils import get_user_role


class RoleAuthenticationForm(AuthenticationForm):
    role = forms.ChoiceField(
        choices=[
            (UserProfile.STUDENT, "Student"),
            (UserProfile.TEACHER, "Teacher"),
            (UserProfile.ADMIN, "Administrator"),
        ],
        initial=UserProfile.STUDENT,
        widget=forms.RadioSelect,
        label="Portal type",
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Enter your username",
                "autocomplete": "username",
                "autofocus": True,
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        )

    def clean(self):
        cleaned_data = super().clean()
        selected_role = cleaned_data.get("role")
        user = self.get_user()
        if user and selected_role and get_user_role(user) != selected_role:
            raise ValidationError(
                "The selected portal does not match this account. Choose the correct role and try again.",
                code="invalid_role",
            )
        return cleaned_data


class StyledForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class AccountCreateForm(StyledForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    reference_id = forms.CharField(
        max_length=30,
        required=False,
        label="Student/Teacher Reference ID",
        help_text="Example: STU-0001 or TCH-0001. Leave blank only for Administrator.",
    )
    display_name = forms.CharField(max_length=120, required=False)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    active = forms.BooleanField(required=False, initial=True)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already in use.")
        return username

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Passwords do not match.")

        role = cleaned.get("role")
        reference = (cleaned.get("reference_id") or "").strip()
        display_name = (cleaned.get("display_name") or "").strip()

        if role == UserProfile.STUDENT:
            if not reference:
                self.add_error("reference_id", "A Student ID is required.")
            else:
                try:
                    student = Student.objects.filter(student_id=reference).first()
                    if student is None and reference.isdigit():
                        student = Student.objects.filter(pk=int(reference)).first()
                except Exception as exc:
                    raise ValidationError(f"Could not connect to the MySQL student database: {exc}")
                if not student:
                    self.add_error("reference_id", "No student with this ID exists in MySQL.")
                else:
                    cleaned["reference_id"] = student.reference_code
                    cleaned["display_name"] = display_name or student.name

        elif role == UserProfile.TEACHER:
            if not reference:
                self.add_error("reference_id", "A Teacher ID is required.")
            else:
                try:
                    teacher = Teacher.objects.filter(employee_id=reference).first()
                    if teacher is None and reference.isdigit():
                        teacher = Teacher.objects.filter(pk=int(reference)).first()
                except Exception as exc:
                    raise ValidationError(f"Could not connect to the PostgreSQL teacher database: {exc}")
                if not teacher:
                    self.add_error("reference_id", "No teacher with this ID exists in PostgreSQL.")
                else:
                    cleaned["reference_id"] = teacher.reference_code
                    cleaned["display_name"] = display_name or teacher.name

        elif role == UserProfile.ADMIN:
            cleaned["reference_id"] = ""
            cleaned["display_name"] = display_name or cleaned.get("username", "")

        reference = cleaned.get("reference_id", "")
        if role and reference and UserProfile.objects.filter(role=role, reference_id=reference).exists():
            self.add_error("reference_id", "An account already exists for this person.")
        return cleaned

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["username"],
            email=data.get("email", ""),
            password=data["password1"],
            is_active=data.get("active", True),
            is_staff=data["role"] == UserProfile.ADMIN,
        )
        UserProfile.objects.create(
            user=user,
            role=data["role"],
            reference_id=data.get("reference_id", ""),
            display_name=data.get("display_name", ""),
        )
        return user


class AccountPasswordForm(StyledForm):
    password1 = forms.CharField(label="New Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return cleaned


class StudentBusCardForm(forms.ModelForm):
    class Meta:
        model = BusCardApplication
        fields = ["phone", "pickup_point", "address", "emergency_contact", "blood_group"]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["pickup_point"].widget.attrs["placeholder"] = "Example: Mirpur 10, Dhanmondi, Uttara"
        self.fields["emergency_contact"].widget.attrs["placeholder"] = "Emergency phone number"
