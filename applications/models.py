from django.db import models
from django.conf import settings
from django.utils import timezone
from academics.models import SubjectBundle, StudentProfile
from datetime import date
import random
import string

class Application(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
        ('WAITLISTED', 'Waitlisted'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    RELATIONSHIP_CHOICES = [
        ('mother', 'Mother'),
        ('father', 'Father'),
        ('guardian', 'Guardian'),
    ]
    
    HEAR_ABOUT_CHOICES = [
        ('social_media', 'Social Media'),
        ('friend', 'Friend/Family'),
        ('school_website', 'School Website'),
        ('radio', 'Radio'),
        ('billboard', 'Billboard'),
        ('other', 'Other'),
    ]
    
    # Reference & Status
    reference_number = models.CharField(max_length=20, unique=True, blank=True)
    submitted_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    # Child Details
    child_full_name = models.CharField(max_length=150, help_text="Full name as on birth certificate")
    child_dob = models.DateField(help_text="Date of birth")
    child_gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    child_nationality = models.CharField(max_length=50, default='Zimbabwean')
    child_id_number = models.CharField(max_length=20, blank=True, help_text="Zimbabwean ID number (if available)")
    current_school = models.CharField(max_length=150, blank=True, help_text="Current school (if transferring)")
    current_form = models.CharField(max_length=20, blank=True, help_text="Current grade/form")
    desired_form = models.CharField(max_length=20, help_text="Desired grade/form (e.g., Form 1, Lower 6)")
    subject_bundle = models.ForeignKey(
        SubjectBundle, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Preferred subject bundle (if known)"
    )
    special_needs = models.TextField(blank=True, help_text="Any special needs or medical conditions")
    
    # Parent/Guardian Details
    parent_full_name = models.CharField(max_length=150)
    parent_relationship = models.CharField(max_length=10, choices=RELATIONSHIP_CHOICES)
    parent_phone = models.CharField(max_length=15, help_text="Zimbabwe number (e.g., 077XXXXXXX)")
    parent_email = models.EmailField()
    parent_address = models.TextField(help_text="Physical address")
    parent_occupation = models.CharField(max_length=100, blank=True)
    parent_employer = models.CharField(max_length=100, blank=True)
    
    # Documents (File Uploads)
    birth_certificate = models.FileField(
        upload_to='applications/birth_certificates/',
        help_text="Upload birth certificate (PDF/JPEG)"
    )
    school_report = models.FileField(
        upload_to='applications/school_reports/',
        blank=True,
        null=True,
        help_text="Upload last school report (PDF/JPEG) - optional"
    )
    child_photo = models.ImageField(
        upload_to='applications/photos/',
        help_text="Upload passport-size photo (JPEG/PNG)"
    )
    parent_id_copy = models.FileField(
        upload_to='applications/parent_ids/',
        blank=True,
        null=True,
        help_text="Upload parent/guardian ID copy (optional)"
    )
    
    # Additional Information
    preferred_start_date = models.DateField(help_text="When would you like your child to start?")
    hear_about_us = models.CharField(max_length=20, choices=HEAR_ABOUT_CHOICES, blank=True)
    comments = models.TextField(blank=True, help_text="Any additional comments or requests")
    
    # Admin fields
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications'
    )
    reviewed_date = models.DateTimeField(null=True, blank=True)
    decline_reason = models.TextField(blank=True, help_text="Reason for declining (if applicable)")
    internal_notes = models.TextField(blank=True, help_text="Internal notes (not visible to parent)")
    
    def __str__(self):
        return f"{self.reference_number} - {self.child_full_name}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate reference number: APP-2026-001
            year = date.today().year
            count = Application.objects.filter(
                reference_number__startswith=f"APP-{year}"
            ).count() + 1
            self.reference_number = f"APP-{year}-{count:03d}"
        super().save(*args, **kwargs)
    
    def accept_application(self, user):
        """Accept the application and create student profile"""
        from academics.models import StudentProfile
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Generate username from reference number
        username = self.reference_number.lower()
        
        # Create user account
        temp_password = ''.join(random.choices(string.digits, k=8))
        user = User.objects.create_user(
            username=username,
            password=temp_password,
            email=self.parent_email,
            full_name=self.child_full_name,
            is_student=True,
            is_active=True
        )
        
        # Create student profile
        profile = StudentProfile.objects.create(
            user=user,
            current_form=self.desired_form,
            subject_bundle=self.subject_bundle,
            enrollment_status='ACCEPTED',
            parent_full_name=self.parent_full_name,
            parent_phone=self.parent_phone,
            parent_email=self.parent_email
        )
        
        # Update application status
        self.status = 'ACCEPTED'
        self.reviewed_by = user
        self.reviewed_date = timezone.now()
        self.save()
        
        return profile, temp_password
    
    def decline_application(self, user, reason):
        """Decline the application"""
        self.status = 'DECLINED'
        self.reviewed_by = user
        self.reviewed_date = timezone.now()
        self.decline_reason = reason
        self.save()
    
    def waitlist_application(self, user):
        """Waitlist the application"""
        self.status = 'WAITLISTED'
        self.reviewed_by = user
        self.reviewed_date = timezone.now()
        self.save()
