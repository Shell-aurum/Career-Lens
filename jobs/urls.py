from django.urls import path
from . import views

urlpatterns = [
    path('api/all/', views.api_get_all_jobs, name='api_get_all_jobs'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
    path('<int:job_id>/apply/', views.apply_for_job, name='apply_job')
]