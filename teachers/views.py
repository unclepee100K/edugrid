from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academics.models import Assignment, Submission, Subject, SchoolTerm


@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        messages.error(request, 'Access denied. Teacher only.')
        return redirect('student_dashboard')

    assignments = Assignment.objects.filter(created_by=request.user).order_by('-created_at')
    pending_submissions = Submission.objects.filter(
        assignment__in=assignments,
        is_marked=False
    ).select_related('student__user', 'assignment')
    recent_marked = Submission.objects.filter(
        assignment__in=assignments,
        is_marked=True
    ).order_by('-submitted_on')[:10]
    subjects = Subject.objects.filter(assignments__created_by=request.user).distinct()

    context = {
        'assignments': assignments,
        'pending_submissions': pending_submissions,
        'recent_marked': recent_marked,
        'subjects': subjects,
        'pending_count': pending_submissions.count(),
    }
    return render(request, 'teachers/dashboard.html', context)


@login_required
def mark_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, assignment__created_by=request.user)
    if request.method == 'POST':
        marks = request.POST.get('marks')
        feedback = request.POST.get('feedback', '')
        if marks:
            try:
                submission.marks_obtained = float(marks)
                submission.feedback = feedback
                submission.is_marked = True
                submission.save()
                messages.success(request, 'Submission marked successfully.')
                return redirect('teacher_dashboard')
            except ValueError:
                messages.error(request, 'Invalid marks.')
    return render(request, 'teachers/mark_submission.html', {'submission': submission})


@login_required
def create_assignment(request):
    if request.method == 'POST':
        subject = get_object_or_404(Subject, id=request.POST.get('subject'))
        term = get_object_or_404(SchoolTerm, id=request.POST.get('term'), is_current=True)
        assignment = Assignment.objects.create(
            subject=subject,
            term=term,
            created_by=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            assignment_type=request.POST.get('assignment_type'),
            max_marks=request.POST.get('max_marks'),
            due_date=request.POST.get('due_date'),
            document=request.FILES.get('document'),
            is_published=True
        )
        messages.success(request, f'Assignment "{assignment.title}" created.')
        return redirect('teacher_dashboard')

    subjects = Subject.objects.all()
    current_term = SchoolTerm.objects.filter(is_current=True).first()
    return render(request, 'teachers/create_assignment.html', {
        'subjects': subjects,
        'current_term': current_term,
        'assignment_types': Assignment.ASSIGNMENT_TYPES,
    })