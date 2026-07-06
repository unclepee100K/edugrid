import requests
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


class NotificationService:
    """Handles SMS and Email notifications"""

    @staticmethod
    def send_sms(phone_number, message):
        """
        Send SMS using AfricasTalking API
        Phone number format: 077XXXXXXX (Zimbabwe)
        """

        # Check if number starts with 0, convert to 263 format
        if phone_number.startswith('0'):
            phone_number = '263' + phone_number[1:]

        # AfricasTalking API credentials (add to settings.py)
        username = getattr(settings, 'AFRICASTALKING_USERNAME', 'sandbox')
        api_key = getattr(settings, 'AFRICASTALKING_API_KEY', 'your_api_key_here')

        # For testing, log instead of actually sending
        if settings.DEBUG:
            print(f"[SMS] To: {phone_number} | Message: {message}")
            return True

        try:
            response = requests.post(
                'https://api.africastalking.com/version1/messaging',
                data={
                    'username': username,
                    'to': phone_number,
                    'message': message,
                },
                headers={
                    'apiKey': api_key,
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            )
            return response.status_code == 200
        except Exception as e:
            print(f"SMS Error: {e}")
            return False

    @staticmethod
    def send_email(to_email, subject, template_name, context):
        """Send email notification"""

        if settings.DEBUG:
            print(f"[EMAIL] To: {to_email} | Subject: {subject}")
            return True

        try:
            html_message = render_to_string(template_name, context)
            send_mail(
                subject,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Email Error: {e}")
            return False

    @staticmethod
    def notify_assignment_submitted(assignment, student):
        """Notify teacher when student submits assignment"""

        # Get subject teacher (for now, we'll use the first teacher who created it)
        if assignment.created_by:
            teacher_email = assignment.created_by.email
            teacher_phone = getattr(assignment.created_by, 'phone_number', None)

            message = f"{student.user.full_name} has submitted '{assignment.title}'."

            if teacher_email:
                NotificationService.send_email(
                    teacher_email,
                    f"Assignment Submitted: {assignment.title}",
                    'emails/assignment_submitted_teacher.html',
                    {'assignment': assignment, 'student': student}
                )

            if teacher_phone:
                NotificationService.send_sms(
                    teacher_phone,
                    f"EduGrid: {student.user.full_name} submitted {assignment.title}"
                )

    @staticmethod
    def notify_parent_report_ready(student):
        """Notify parent when termly report is ready"""

        # Get parent contact from student profile
        parent_phone = student.parent_phone
        parent_email = student.parent_email

        if parent_phone:
            NotificationService.send_sms(
                parent_phone,
                f"EduGrid: Termly report for {student.user.full_name} is ready. Log in to view."
            )

        if parent_email:
            NotificationService.send_email(
                parent_email,
                f"Termly Report: {student.user.full_name}",
                'emails/report_ready.html',
                {'student': student}
            )