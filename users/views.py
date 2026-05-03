import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

# Model Imports
from .models import User, JobSeeker, Recruiter
from ai_engine.models import Resume
from jobs.models import JobListing, Application

# --- AUTHENTICATION VIEWS ---

def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        # Create base User
        user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
        
        if role == 'job_seeker':
            user.is_job_seeker = True
            user.save()
            JobSeeker.objects.create(user=user)
        elif role == 'recruiter':
            user.is_recruiter = True
            user.save()
            company_name = request.POST.get('company_name')
            Recruiter.objects.create(user=user, company_name=company_name, is_premium=False)
            
        login(request, user)
        return redirect('dashboard')

    return render(request, 'users/index.html') 

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'users/index.html', {'error_message': 'Invalid email or password.'})
            
    return render(request, 'users/index.html')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

# --- DASHBOARD & MODE VIEWS ---

@login_required
def dashboard_view(request):
    # Fetch user applications to show status on the dashboard
    user_applications = Application.objects.filter(applicant=request.user).order_by('-id')
    return render(request, 'users/dashboard.html', {'applications': user_applications})

@login_required
def toggle_user_mode(request):
    """Instantly switch between Job Seeker and Recruiter roles."""
    if request.method == 'POST':
        request.user.is_recruiter = not request.user.is_recruiter
        request.user.save()
    return redirect('dashboard')

# --- RECRUITER FUNCTIONALITIES ---

@login_required
def post_job_view(request):
    """Handles creating new job listings."""
    if not getattr(request.user, 'is_recruiter', False):
        return redirect('dashboard')
        
    if request.method == 'POST':
        JobListing.objects.create(
            title=request.POST.get('title'),
            company_name=request.POST.get('company_name'),
            work_mode=request.POST.get('location'), 
            employment_type=request.POST.get('job_type'), 
            description=request.POST.get('description'),
            company_type="Technology" 
        )
        return redirect('dashboard')
        
    return render(request, 'users/post_jobs.html')

@login_required
def talent_pool_view(request):
    """ATS Talent Pool view for recruiters."""
    if not getattr(request.user, 'is_recruiter', False):
        return redirect('dashboard')
        
    applications = Application.objects.all().order_by('-id')
    
    apps_data = []
    for app in applications:
        int_date = app.interview_date.strftime("%b %d, %Y %I:%M %p") if app.interview_date else None
        apps_data.append({
            'id': app.id,
            'name': app.applicant.get_full_name() or app.applicant.username,
            'role': app.job.title,
            'match': 92, # Placeholder for AI logic
            'status': app.status,
            'date': "Recent",
            'interviewDate': int_date
        })
        
    return render(request, 'users/talent.html', {'applications_json': json.dumps(apps_data)})

@login_required
@require_POST
def update_application_status(request, app_id):
    """API for status updates and interview scheduling."""
    if not getattr(request.user, 'is_recruiter', False):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        application = Application.objects.get(id=app_id)
        
        application.status = new_status
        if new_status == 'scheduled':
            application.interview_date = timezone.now() + datetime.timedelta(days=3)
        elif new_status == 'approved':
            application.interview_date = None # Clear date if reverted from scheduled
            
        application.save()
        return JsonResponse({'success': True})
        
    except Application.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

@login_required
def cancel_interview(request, app_id):
    """Allows a recruiter to revert an interview back to 'approved' status."""
    if not getattr(request.user, 'is_recruiter', False):
        return redirect('dashboard')
    
    application = get_object_or_404(Application, id=app_id)
    application.status = 'approved'
    application.interview_date = None
    application.save()
    messages.info(request, "Interview cancelled. Candidate moved back to pool.")
    return redirect('dashboard')


# --- JOB SEEKER FUNCTIONALITIES ---

@login_required
def resume_report_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    word_count = len(resume.parsed_text.split()) if resume.parsed_text else 0
    jobs = JobListing.objects.all().order_by('-posted_date')
    
    return render(request, 'users/resume_report.html', {
        'resume': resume,
        'word_count': word_count,
        'jobs': jobs
    })

# In users/views.py

@login_required
def cancel_application(request, app_id):
    """Allows a seeker to withdraw their application."""
    application = get_object_or_404(Application, id=app_id, applicant=request.user)
    application.delete()
    messages.success(request, "Application withdrawn successfully.")
    return redirect('dashboard')

@login_required
def explore_view(request):
    jobs = JobListing.objects.all().order_by('-posted_date')
    return render(request, 'users/explore.html', {'jobs': jobs})

@login_required
def analyse_resume_view(request):
    return render(request, 'users/analyse_resume.html')