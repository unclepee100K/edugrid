from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('apply/', views.apply, name='apply'),
    path('confirmation/<str:ref>/', views.application_confirmation, name='application_confirmation'),
    path('status/', views.application_status_check, name='application_status_check'),
    
    # Admin URLs
    path('admin/', views.admin_applications, name='admin_applications'),
    path('admin/<int:app_id>/', views.application_detail, name='application_detail'),
]
