from django.urls import path
from . import views

urlpatterns = [
    path('api/all/', views.api_get_all_jobs, name='api_get_all_jobs'),
    path('<int:job_id>/apply/', views.apply_job_view, name='apply_job'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
]