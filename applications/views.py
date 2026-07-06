from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Application
from .forms import ApplicationForm
from utils.notifications import NotificationService

def apply(request):
    """Public application form for parents"""
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save()
            
            # Send confirmation to parent
            try:
                # SMS
                NotificationService.send_sms(
                    application.parent_phone,
                    f"EduGrid: Application received. Ref: {application.reference_number}. We'll contact you within 7 days."
                )
                # Email
                subject = f"Application Received - {application.reference_number}"
                html_message = render_to_string('applications/email_confirmation.html', {
                    'application': application
                })
                send_mail(
                    subject,
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [application.parent_email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                # Log error but don't stop the process
                print(f"Notification error: {e}")
            
            messages.success(request, f'Your application has been submitted successfully. Reference: {application.reference_number}')
            return redirect('application_confirmation', ref=application.reference_number)
    else:
        form = ApplicationForm()
    
    return render(request, 'applications/apply.html', {'form': form})

def application_confirmation(request, ref):
    """Confirmation page after application submission"""
    application = get_object_or_404(Application, reference_number=ref)
    return render(request, 'applications/confirmation.html', {'application': application})

def application_status_check(request):
    """Public page to check application status"""
    if request.method == 'POST':
        ref = request.POST.get('reference_number')
        try:
            application = Application.objects.get(reference_number=ref)
            return render(request, 'applications/status.html', {'application': application})
        except Application.DoesNotExist:
            messages.error(request, 'Application not found. Please check your reference number.')
    return render(request, 'applications/status_check.html')

@staff_member_required
def admin_applications(request):
    """Admin dashboard for managing applications"""
    applications = Application.objects.all().order_by('-submitted_date')
    pending_count = Application.objects.filter(status='PENDING').count()
    accepted_count = Application.objects.filter(status='ACCEPTED').count()
    declined_count = Application.objects.filter(status='DECLINED').count()
    waitlisted_count = Application.objects.filter(status='WAITLISTED').count()
    
    context = {
        'applications': applications,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'declined_count': declined_count,
        'waitlisted_count': waitlisted_count,
    }
    return render(request, 'applications/admin_dashboard.html', context)

@staff_member_required
def application_detail(request, app_id):
    """View and manage a single application"""
    application = get_object_or_404(Application, id=app_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accept':
            try:
                profile, temp_password = application.accept_application(request.user)
                messages.success(request, f'Application accepted. Student ID: {profile.student_id}')
                
                # Notify parent
                NotificationService.send_sms(
                    application.parent_phone,
                    f"EduGrid: Congratulations! Your child has been accepted. Student ID: {profile.student_id}. Login: {profile.user.username}"
                )
                send_mail(
                    'Application Accepted - Welcome to EduGrid',
                    f'Your child has been accepted to EduGrid School.\n\nStudent ID: {profile.student_id}\nUsername: {profile.user.username}\nPassword: {temp_password}\n\nPlease login and change your password.',
                    settings.DEFAULT_FROM_EMAIL,
                    [application.parent_email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.error(request, f'Error accepting application: {e}')
                
        elif action == 'decline':
            reason = request.POST.get('decline_reason', 'No reason provided')
            application.decline_application(request.user, reason)
            messages.success(request, 'Application declined.')
            
            # Notify parent
            NotificationService.send_sms(
                application.parent_phone,
                f"EduGrid: Your application has been declined. Reason: {reason}"
            )
            send_mail(
                'Application Update - EduGrid',
                f'Your application has been declined.\n\nReason: {reason}\n\nContact the school for more information.',
                settings.DEFAULT_FROM_EMAIL,
                [application.parent_email],
                fail_silently=False,
            )
            
        elif action == 'waitlist':
            application.waitlist_application(request.user)
            messages.success(request, 'Application waitlisted.')
            NotificationService.send_sms(
                application.parent_phone,
                f"EduGrid: Your application has been waitlisted. We will contact you when a spot opens."
            )
            
        return redirect('application_detail', app_id=app_id)
    
    return render(request, 'applications/admin_detail.html', {'application': application})
