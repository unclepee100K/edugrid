from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date
import re


# ------------------------------------------------------------
# 1. SUBJECT MODEL
# ------------------------------------------------------------
class Subject(models.Model):
    LEVEL_CHOICES = [
        ('O', 'O-Level'),
        ('A', 'A-Level'),
    ]

    name = models.CharField(max_length=100)  # e.g., "Mathematics"
    code = models.CharField(max_length=20, unique=True)  # e.g., "MATH-O-01"
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES, default='O')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

    class Meta:
        ordering = ['name']


# ------------------------------------------------------------
# 2. SUBJECT BUNDLE (e.g., Science Bundle, Commercials Bundle)
# ------------------------------------------------------------
class SubjectBundle(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Science Bundle"
    description = models.TextField(blank=True)
    subjects = models.ManyToManyField(Subject, related_name='bundles')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# ------------------------------------------------------------
# 3. SCHOOL TERM (Term 1, 2, 3 with Zimbabwean calendar)
# ------------------------------------------------------------
class SchoolTerm(models.Model):
    TERM_CHOICES = [
        (1, 'Term 1'),
        (2, 'Term 2'),
        (3, 'Term 3'),
    ]

    term_number = models.IntegerField(choices=TERM_CHOICES)
    academic_year = models.CharField(max_length=9)  # e.g., "2026"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_term_number_display()} - {self.academic_year}"

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("Start date must be before end date.")

    class Meta:
        unique_together = ['term_number', 'academic_year']
        ordering = ['academic_year', 'term_number']


# ------------------------------------------------------------
# 4. STUDENT PROFILE (Links CustomUser to Academic Data)
# ------------------------------------------------------------
class StudentProfile(models.Model):
    FORM_CHOICES = [
        ('Form 1', 'Form 1'),
        ('Form 2', 'Form 2'),
        ('Form 3', 'Form 3'),
        ('Form 4', 'Form 4'),
        ('Lower 6', 'Lower 6'),
        ('Upper 6', 'Upper 6'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    ]

    # Link to the Custom User model (created earlier)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    # Auto-generated Student ID: e.g., GRD-2026-SCI-001
    student_id = models.CharField(max_length=20, unique=True, blank=True)

    # Academic Details
    current_form = models.CharField(max_length=10, choices=FORM_CHOICES)
    subject_bundle = models.ForeignKey(
        SubjectBundle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )
    enrollment_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    date_enrolled = models.DateField(auto_now_add=True)

    # Guardian/Parent Details (for the parent portal)
    parent_full_name = models.CharField(max_length=150, blank=True)
    parent_phone = models.CharField(max_length=15, blank=True)  # Zimbabwe format: 077XXXXXXX
    parent_email = models.EmailField(blank=True)

    # Optional: Profile picture
    profile_picture = models.ImageField(upload_to='student_profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name} ({self.student_id})"

    def save(self, *args, **kwargs):
        # Auto-generate the Student ID if it's blank
        if not self.student_id:
            # Get the year from the current date
            year = date.today().year

            # Get the bundle code (first 3 letters of bundle name, uppercase)
            bundle_code = "GEN"  # Default fallback
            if self.subject_bundle:
                # Extract first 3 letters, e.g., "SCI" from "Science Bundle"
                words = self.subject_bundle.name.split()
                if words:
                    bundle_code = ''.join(word[0] for word in words[:2]).upper()
                    bundle_code = bundle_code[:3]  # Max 3 characters
                else:
                    bundle_code = self.subject_bundle.name[:3].upper()

            # Count existing students in the same year and bundle to create sequential number
            existing = StudentProfile.objects.filter(
                student_id__startswith=f"GRD-{year}-{bundle_code}-"
            ).count()

            # Increment by 1 and pad to 3 digits (e.g., 001, 012, 123)
            sequence = existing + 1
            self.student_id = f"GRD-{year}-{bundle_code}-{sequence:03d}"

        # Ensure the CustomUser's is_student flag is set to True
        if not self.user.is_student:
            self.user.is_student = True
            self.user.save()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_enrolled']


# ------------------------------------------------------------
# 5. ASSIGNMENT (Uploaded by Teacher)
# ------------------------------------------------------------
class Assignment(models.Model):
    ASSIGNMENT_TYPES = [
        ('CA', 'Continuous Assessment (Test)'),
        ('PR', 'Practical/Project'),
        ('HW', 'Homework'),
        ('EX', 'End of Term Exam'),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    term = models.ForeignKey(
        SchoolTerm,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assignments'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assignment_type = models.CharField(max_length=2, choices=ASSIGNMENT_TYPES, default='HW')

    # Document upload (the material the student must read or use)
    document = models.FileField(
        upload_to='assignment_documents/',
        blank=True,
        null=True
    )

    max_marks = models.FloatField(default=100)
    due_date = models.DateTimeField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.subject.name} ({self.term})"

    @property
    def is_overdue(self):
        from django.utils.timezone import now
        return now() > self.due_date

    class Meta:
        ordering = ['-created_at']


# ------------------------------------------------------------
# 6. SUBMISSION (Student submits their work)
# ------------------------------------------------------------
class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    # The file the student uploads (e.g., PDF, Word document)
    submitted_file = models.FileField(
        upload_to='student_submissions/',
        blank=True,
        null=True
    )
    text_response = models.TextField(blank=True, help_text="If no file, student can type response here.")

    submitted_on = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    is_marked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.user.full_name} - {self.assignment.title}"

    @property
    def is_late(self):
        from django.utils.timezone import now
        return self.submitted_on > self.assignment.due_date

    class Meta:
        ordering = ['-submitted_on']
        # Ensure one submission per student per assignment
        unique_together = ['assignment', 'student']