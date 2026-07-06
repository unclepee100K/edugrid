from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from .views import landing_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('teacher/', include('teachers.urls')),
    path('parent/', include('school_parent.urls')),
    path('reports/', include('reports.urls')),
    path('applications/', include('applications.urls')),

    # Login - shows the login page
    path('login/', LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=False,
        next_page='/'
    ), name='login'),

    # Logout - redirects to landing page, allows GET for simplicity
    path('logout/', LogoutView.as_view(
        next_page='landing_page',
        http_method_names=['get', 'post']
    ), name='logout'),

    # Root - landing page
    path('', landing_page, name='landing_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
