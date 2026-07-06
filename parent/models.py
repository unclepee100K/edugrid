from django.db import models
from django.conf import settings
from academics.models import StudentProfile
import random
import string


class ParentAccess(models.Model):
    """Parent access PIN for viewing child's progress"""

    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='parent_access'
    )
    pin_code = models.CharField(max_length=6)  # 4-6 digit PIN
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.full_name} - PIN: {self.pin_code}"

    def save(self, *args, **kwargs):
        if not self.pin_code:
            # Generate a 4-digit PIN
            self.pin_code = ''.join(random.choices(string.digits, k=4))
        super().save(*args, **kwargs)