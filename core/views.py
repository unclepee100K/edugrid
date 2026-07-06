from django.shortcuts import render, redirect

def landing_page(request):
    """Landing page – shows login info, but redirects if user is already logged in."""
    if request.user.is_authenticated:
        # Redirect to appropriate dashboard based on role
        if request.user.is_superuser or getattr(request.user, 'is_admin_staff', False):
            return redirect('/admin/')
        elif getattr(request.user, 'is_teacher', False):
            return redirect('/teacher/')
        elif getattr(request.user, 'is_student', False):
            return redirect('/dashboard/')
        else:
            return redirect('/dashboard/')  # fallback
    return render(request, 'landing.html')