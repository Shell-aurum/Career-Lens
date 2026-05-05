from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('signup'), name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # The route for the Job Board
    path('explore/', views.explore_view, name='explore'),
    path('analyse-resume/', views.analyse_resume_view, name='analyse_resume'),
   
    # The dedicated report page
    path('resume/report/<int:resume_id>/', views.resume_report_view, name='resume_report'),

    # Mode Switching toggle
    path('toggle-mode/', views.toggle_user_mode, name='toggle_mode'),
    path('talent-pool/', views.talent_pool_view, name='talent_pool'),
    
    path('update-status/<int:app_id>/', views.update_application_status, name='update_status'),
    path('post-job/', views.post_job_view, name='post_job'),

    # Cancellation route for job applications
    path('cancel-application/<int:app_id>/', views.cancel_application, name='cancel_application'),
    path('cancel-interview/<int:app_id>/', views.cancel_interview, name='cancel_interview'),

    #cancel job post
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
]