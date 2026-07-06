from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_dashboard, name='teacher_dashboard'),
    path('mark/<int:submission_id>/', views.mark_submission, name='mark_submission'),
    path('create-assignment/', views.create_assignment, name='create_assignment'),
]