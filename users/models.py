from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # The `username`, `email`, `password` come from AbstractUser.
    # We add extra fields for roles:
    full_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Role Flags (Boolean)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_admin_staff = models.BooleanField(default=False)  # School Admin

    def __str__(self):
        return f"{self.username} ({self.full_name})"