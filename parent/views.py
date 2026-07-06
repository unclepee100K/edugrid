from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from academics.models import StudentProfile, Submission, SchoolTerm
from .models import ParentAccess


def parent_login(request):
    """Parent enters student ID and PIN to view progress"""

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        pin = request.POST.get('pin')

        try:
            student = StudentProfile.objects.get(student_id=student_id)
            parent_access = ParentAccess.objects.get(student=student, pin_code=pin, is_active=True)

            # Store in session
            request.session['parent_student_id'] = student.id
            return redirect('parent_dashboard')
        except (StudentProfile.DoesNotExist, ParentAccess.DoesNotExist):
            messages.error(request, 'Invalid Student ID or PIN. Please try again.')

    return render(request, 'parent/login.html')


def parent_dashboard(request):
    """Parent sees child's progress (read-only)"""

    student_id = request.session.get('parent_student_id')
    if not student_id:
        return redirect('parent_login')

    student = get_object_or_404(StudentProfile, id=student_id)

    # Get student data (same as student dashboard but read-only)
    submissions = Submission.objects.filter(
        student=student,
        is_marked=True
    )

    overall_avg = submissions.aggregate(Avg('marks_obtained'))['marks_obtained__avg']

    context = {
        'student': student,
        'overall_average': round(overall_avg, 1) if overall_avg else 0,
        'submissions': submissions,
        'total_submissions': submissions.count(),
    }

    return render(request, 'parent/dashboard.html', context)