from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='student_dashboard'),
    path('assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('progress/', views.view_progress, name='view_progress'),
]