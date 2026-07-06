from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from academics.models import Assignment, Submission, Subject
from django.db.models import Count, Q


@login_required
def teacher_dashboard(request):
    # Ensure user is a teacher
    if not request.user.is_teacher:
        messages.error(request, 'Access denied. Teacher only.')
        return redirect('student_dashboard')

    # Assignments created by this teacher
    assignments = Assignment.objects.filter(created_by=request.user).order_by('-created_at')

    # Pending submissions (for this teacher's assignments)
    pending_submissions = Submission.objects.filter(
        assignment__in=assignments,
        is_marked=False
    ).select_related('student__user', 'assignment')

    # Recent marked submissions
    recent_marked = Submission.objects.filter(
        assignment__in=assignments,
        is_marked=True
    ).order_by('-submitted_on')[:10]

    # Subject list (for filtering)
    subjects = Subject.objects.filter(
        assignments__created_by=request.user
    ).distinct()

    context = {
        'assignments': assignments,
        'pending_submissions': pending_submissions,
        'recent_marked': recent_marked,
        'subjects': subjects,
        'pending_count': pending_submissions.count(),
    }
    return render(request, 'teacher/dashboard.html', context)


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
                messages.error(request, 'Invalid marks. Please enter a number.')

    return render(request, 'teacher/mark_submission.html', {'submission': submission})


@login_required
def create_assignment(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        title = request.POST.get('title')
        description = request.POST.get('description')
        assignment_type = request.POST.get('assignment_type')
        max_marks = request.POST.get('max_marks')
        due_date = request.POST.get('due_date')
        document = request.FILES.get('document')
        term_id = request.POST.get('term')

        term = get_object_or_404(SchoolTerm, id=term_id, is_current=True)
        subject = get_object_or_404(Subject, id=subject_id)

        assignment = Assignment.objects.create(
            subject=subject,
            term=term,
            created_by=request.user,
            title=title,
            description=description,
            assignment_type=assignment_type,
            max_marks=max_marks,
            due_date=due_date,
            document=document,
            is_published=True
        )
        messages.success(request, f'Assignment "{title}" created successfully.')
        return redirect('teacher_dashboard')

    # GET – show form
    subjects = Subject.objects.all()
    current_term = SchoolTerm.objects.filter(is_current=True).first()
    return render(request, 'teacher/create_assignment.html', {
        'subjects': subjects,
        'current_term': current_term,
        'assignment_types': Assignment.ASSIGNMENT_TYPES,
    })