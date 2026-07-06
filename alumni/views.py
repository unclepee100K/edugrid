from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from academics.models import StudentProfile
from .models import AlumniProfile

@staff_member_required
def graduate_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    if request.method == 'POST':
        graduation_year = request.POST.get('graduation_year')
        final_form = request.POST.get('final_form')
        alumni, created = AlumniProfile.objects.get_or_create(
            student=student,
            defaults={
                'graduation_year': graduation_year,
                'final_form': final_form,
                'email': student.user.email,
                'phone': student.parent_phone,
            }
        )
        # Optionally disable student access to normal dashboard
        # student.user.is_student = False
        # student.user.save()
        return redirect('admin:index')
    return render(request, 'alumni/graduate.html', {'student': student})