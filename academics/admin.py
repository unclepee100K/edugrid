from django.contrib import admin
from .models import Subject, SubjectBundle, SchoolTerm, StudentProfile, Assignment, Submission

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'level']
    search_fields = ['name', 'code']

@admin.register(SubjectBundle)
class SubjectBundleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    filter_horizontal = ['subjects']

@admin.register(SchoolTerm)
class SchoolTermAdmin(admin.ModelAdmin):
    list_display = ['term_number', 'academic_year', 'start_date', 'end_date', 'is_current']
    list_editable = ['is_current']

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'current_form', 'subject_bundle', 'enrollment_status']
    list_filter = ['enrollment_status', 'current_form', 'subject_bundle']
    search_fields = ['student_id', 'user__username', 'user__full_name']
    readonly_fields = ['student_id']  # ID is auto-generated, can't edit manually

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'term', 'due_date', 'is_published']
    list_filter = ['subject', 'term', 'assignment_type', 'is_published']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submitted_on', 'marks_obtained', 'is_marked']
    list_filter = ['is_marked', 'assignment__subject']