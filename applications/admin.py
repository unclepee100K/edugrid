from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'child_full_name', 'desired_form', 'status', 'submitted_date']
    list_filter = ['status', 'desired_form', 'submitted_date']
    search_fields = ['reference_number', 'child_full_name', 'parent_full_name', 'parent_phone', 'parent_email']
    readonly_fields = ['reference_number', 'submitted_date']
    fieldsets = (
        ('Application Status', {
            'fields': ('reference_number', 'status', 'submitted_date', 'reviewed_by', 'reviewed_date', 'decline_reason', 'internal_notes')
        }),
        ('Child Details', {
            'fields': ('child_full_name', 'child_dob', 'child_gender', 'child_nationality', 'child_id_number', 
                      'current_school', 'current_form', 'desired_form', 'subject_bundle', 'special_needs')
        }),
        ('Parent/Guardian Details', {
            'fields': ('parent_full_name', 'parent_relationship', 'parent_phone', 'parent_email', 
                      'parent_address', 'parent_occupation', 'parent_employer')
        }),
        ('Documents', {
            'fields': ('birth_certificate', 'school_report', 'child_photo', 'parent_id_copy')
        }),
        ('Additional Information', {
            'fields': ('preferred_start_date', 'hear_about_us', 'comments')
        }),
    )
