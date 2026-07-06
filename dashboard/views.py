from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count, Q
from academics.models import StudentProfile, Assignment, Submission, SchoolTerm
from django.utils import timezone
import json


@login_required
def student_dashboard(request):
    """Main dashboard for students showing progress overview"""

    # Get the student profile
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return render(request, 'dashboard/error.html', {
            'message': 'Your student profile has not been set up yet. Please contact administration.'
        })

    # Get current term
    current_term = SchoolTerm.objects.filter(is_current=True).first()

    # Get upcoming assignments (due in next 7 days)
    upcoming_assignments = Assignment.objects.filter(
        is_published=True,
        due_date__gte=timezone.now(),
        due_date__lte=timezone.now() + timezone.timedelta(days=7)
    ).order_by('due_date')[:5]

    # Get pending submissions (assignments the student hasn't submitted yet)
    submitted_assignments = Submission.objects.filter(
        student=student_profile
    ).values_list('assignment_id', flat=True)

    pending_assignments = Assignment.objects.filter(
        is_published=True,
        due_date__gte=timezone.now()
    ).exclude(
        id__in=submitted_assignments
    ).order_by('due_date')[:5]

    # Get recent submissions with marks
    recent_submissions = Submission.objects.filter(
        student=student_profile,
        is_marked=True
    ).order_by('-submitted_on')[:5]

    # Calculate overall performance (average marks)
    all_submissions = Submission.objects.filter(
        student=student_profile,
        is_marked=True
    )

    overall_average = all_submissions.aggregate(Avg('marks_obtained'))['marks_obtained__avg']

    # Subject performance breakdown
    subject_performance = []
    subjects = student_profile.subject_bundle.subjects.all() if student_profile.subject_bundle else []

    for subject in subjects:
        subject_submissions = all_submissions.filter(assignment__subject=subject)
        if subject_submissions.exists():
            avg = subject_submissions.aggregate(Avg('marks_obtained'))['marks_obtained__avg']
            subject_performance.append({
                'subject': subject.name,
                'average': round(avg, 1) if avg else 0,
                'submissions': subject_submissions.count()
            })

    context = {
        'student': student_profile,
        'current_term': current_term,
        'upcoming_assignments': upcoming_assignments,
        'pending_assignments': pending_assignments,
        'recent_submissions': recent_submissions,
        'overall_average': round(overall_average, 1) if overall_average else 0,
        'subject_performance': subject_performance,
        'total_submissions': all_submissions.count(),
        'marked_submissions': all_submissions.filter(is_marked=True).count(),
    }

    return render(request, 'dashboard/student_dashboard.html', context)


@login_required
def assignment_detail(request, assignment_id):
    """View a specific assignment with submission form"""

    assignment = get_object_or_404(Assignment, id=assignment_id, is_published=True)
    student_profile = StudentProfile.objects.get(user=request.user)

    # Check if student has already submitted
    existing_submission = Submission.objects.filter(
        assignment=assignment,
        student=student_profile
    ).first()

    if request.method == 'POST' and not existing_submission:
        # Handle file upload or text response
        submitted_file = request.FILES.get('submitted_file')
        text_response = request.POST.get('text_response', '')

        submission = Submission.objects.create(
            assignment=assignment,
            student=student_profile,
            submitted_file=submitted_file,
            text_response=text_response
        )

        # TODO: Send notification to teacher
        # TODO: Send SMS confirmation to student

        return render(request, 'dashboard/assignment_submitted.html', {
            'assignment': assignment,
            'submission': submission
        })

    context = {
        'assignment': assignment,
        'existing_submission': existing_submission,
        'is_overdue': assignment.is_overdue,
    }

    return render(request, 'dashboard/assignment_detail.html', context)


@login_required
def view_progress(request):
    """Full academic progress view with charts"""

    student_profile = StudentProfile.objects.get(user=request.user)

    # Get all marked submissions
    submissions = Submission.objects.filter(
        student=student_profile,
        is_marked=True
    ).select_related('assignment', 'assignment__subject')

    # Group by subject
    subject_data = {}
    for sub in submissions:
        subject_name = sub.assignment.subject.name
        if subject_name not in subject_data:
            subject_data[subject_name] = {
                'marks': [],
                'assignments': [],
                'total': 0,
                'count': 0
            }
        subject_data[subject_name]['marks'].append(sub.marks_obtained)
        subject_data[subject_name]['assignments'].append(sub.assignment.title)
        subject_data[subject_name]['total'] += sub.marks_obtained
        subject_data[subject_name]['count'] += 1

    # Calculate averages for each subject
    for subject in subject_data:
        subject_data[subject]['average'] = round(
            subject_data[subject]['total'] / subject_data[subject]['count'], 1
        ) if subject_data[subject]['count'] > 0 else 0

    # Generate data for charts (using Chart.js)
    chart_labels = list(subject_data.keys())
    chart_data = [subject_data[s]['average'] for s in chart_labels]

    # Termly progress (by term)
    term_data = {}
    for sub in submissions:
        term = sub.assignment.term
        term_key = f"{term.term_number}-{term.academic_year}"
        if term_key not in term_data:
            term_data[term_key] = {'marks': [], 'total': 0, 'count': 0}
        term_data[term_key]['marks'].append(sub.marks_obtained)
        term_data[term_key]['total'] += sub.marks_obtained
        term_data[term_key]['count'] += 1

    for term in term_data:
        term_data[term]['average'] = round(
            term_data[term]['total'] / term_data[term]['count'], 1
        ) if term_data[term]['count'] > 0 else 0

    context = {
        'student': student_profile,
        'subject_data': subject_data,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'term_labels': json.dumps(list(term_data.keys())),
        'term_data': json.dumps([term_data[t]['average'] for t in term_data]),
        'total_submissions': submissions.count(),
        'overall_average': round(sum([s.marks_obtained for s in submissions]) / len(submissions),
                                 1) if submissions else 0,
    }

    return render(request, 'dashboard/progress_view.html', context)