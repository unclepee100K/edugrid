from django import forms
from .models import Application
from academics.models import SubjectBundle

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        exclude = ['reference_number', 'status', 'reviewed_by', 'reviewed_date', 'decline_reason', 'internal_notes']
        widgets = {
            'child_dob': forms.DateInput(attrs={'type': 'date'}),
            'preferred_start_date': forms.DateInput(attrs={'type': 'date'}),
            'child_gender': forms.RadioSelect,
            'parent_relationship': forms.RadioSelect,
            'comments': forms.Textarea(attrs={'rows': 4}),
            'special_needs': forms.Textarea(attrs={'rows': 3}),
            'parent_address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set placeholder text for file fields
        self.fields['birth_certificate'].help_text = "Upload PDF or JPEG (max 5MB)"
        self.fields['school_report'].help_text = "Upload PDF or JPEG (max 5MB) - optional"
        self.fields['child_photo'].help_text = "Upload JPEG or PNG (max 2MB)"
        self.fields['parent_id_copy'].help_text = "Upload PDF or JPEG (max 5MB) - optional"
