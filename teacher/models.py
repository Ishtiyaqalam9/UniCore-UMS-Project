from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Teacher(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("On Leave", "On Leave"),
        ("Retired", "Retired"),
        ("Inactive", "Inactive"),
    ]

    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100, default="")
    age = models.PositiveSmallIntegerField(
        default=25,
        validators=[MinValueValidator(20), MaxValueValidator(100)],
    )
    subject = models.CharField(max_length=100, default="")
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    email = models.EmailField(default="")
    phone = models.CharField(max_length=20, default="")
    address = models.TextField(blank=True)
    joining_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="Active")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["employee_id", "name"]

    @property
    def reference_code(self):
        return self.employee_id or str(self.pk)

    def save(self, *args, **kwargs):
        creating_code = not self.employee_id
        super().save(*args, **kwargs)
        if creating_code:
            self.employee_id = f"TCH-{self.pk:04d}"
            type(self).objects.filter(pk=self.pk).update(employee_id=self.employee_id)

    def __str__(self):
        return f"{self.reference_code} - {self.name}"
