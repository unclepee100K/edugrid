from django.db import models
from django.conf import settings
from academics.models import StudentProfile


class AlumniProfile(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='alumni')
    graduation_year = models.IntegerField()
    final_form = models.CharField(max_length=10)  # Form 4 or Upper 6

    # Career tracking
    current_occupation = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=100, blank=True)
    course = models.CharField(max_length=100, blank=True)
    working = models.BooleanField(default=False)
    company = models.CharField(max_length=100, blank=True)

    # Contact info for alumni network
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)

    # Portal access
    can_access_portal = models.BooleanField(default=True)

    def __str__(self):
        return f"Alumni: {self.student.user.full_name} ({self.graduation_year})"