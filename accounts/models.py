from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    ADMIN = "ADMIN"
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ROLE_CHOICES = [
        (ADMIN, "Administrator"),
        (STUDENT, "Student"),
        (TEACHER, "Teacher"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ums_profile",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    reference_id = models.CharField(
        max_length=30,
        blank=True,
        help_text="Student ID from MySQL or Teacher ID from PostgreSQL.",
    )
    display_name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["role", "reference_id", "user__username"]
        constraints = [
            models.UniqueConstraint(
                fields=["role", "reference_id"],
                condition=~models.Q(reference_id=""),
                name="unique_role_reference_account",
            )
        ]

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
