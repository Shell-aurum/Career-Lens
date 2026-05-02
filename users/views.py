from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from .models import User, JobSeeker, Recruiter
from ai_engine.models import Resume
from django.contrib.auth.decorators import login_required
from jobs.models import JobListing

@login_required
def resume_report_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    word_count = len(resume.parsed_text.split()) if resume.parsed_text else 0

    # Fetch all live jobs from the database
    jobs = JobListing.objects.all().order_by('-posted_date')

    context = {
        'resume': resume,
        'word_count': word_count,
        'jobs': jobs # Passes the live QuerySet to the template
    }
    return render(request, 'users/resume_report.html', context)

def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        # 1. Create the base User (this automatically hashes the password)
        # Using email as the username
        user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
        
        # 2. Check the role and create the corresponding profile
        if role == 'job_seeker':
            user.is_job_seeker = True
            user.save()
            JobSeeker.objects.create(user=user)
            
        elif role == 'recruiter':
            user.is_recruiter = True
            user.save()
            company_name = request.POST.get('company_name')
            # By default, a new recruiter does not have premium status
            Recruiter.objects.create(user=user, company_name=company_name, is_premium=False)
            
        # Log the user in immediately after signup
        login(request, user)
        return redirect('dashboard') # Redirect to the dashboard page after success

    # If it's a GET request, just render the HTML page
    return render(request, 'users/index.html') 

def dashboard_view(request):
    return render(request, 'users/dashboard.html') # Placeholder for your dashboard


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Django's built-in authentication system checks the database
        # Note: Since we set the username to be the email during signup, we pass it as 'username'
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Validation passed! Log them in.
            login(request, user)
            return redirect('dashboard') # Redirects to your main.html page
        else:
            # Validation failed. Send an error back to the HTML template.
            return render(request, 'users/index.html', {'error_message': 'Invalid email or password.'})
            
    # If it's a GET request, just load the page
    return render(request, 'users/index.html')




# ... your other views ...

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home') # Sends them back to the login page
    

# Ensure only logged-in users can see the job board
@login_required
def explore_view(request):
    return render(request, 'users/explore.html')

@login_required
def analyse_resume_view(request):
    # This view just displays the upload page. 
    # Later, we will point the HTML form to POST directly to the ai_engine.
    return render(request, 'users/analyse_resume.html')

@login_required
def toggle_user_mode(request):
    """Allows a user to instantly switch between Job Seeker and Recruiter modes."""
    if request.method == 'POST':
        # Flip the boolean
        request.user.is_recruiter = not request.user.is_recruiter
        request.user.save()
        
    # Redirect back to dashboard
    return redirect('dashboard')

@login_required
def talent_pool_view(request):
    """Renders the ATS Talent Pool with REAL database applications."""
    if not getattr(request.user, 'is_recruiter', False):
        return redirect('dashboard')
        
    # Fetch real applications (assuming your Job model connects to the recruiter user)
    # If your Job model doesn't have a specific recruiter field, you can use .all() for testing
    applications = Application.objects.all().order_by('-id')
    
    # Package the real database info into a format our JavaScript can read
    apps_data = []
    for app in applications:
        # Format the date if it exists, otherwise leave empty
        int_date = app.interview_date.strftime("%b %d, %Y %I:%M %p") if app.interview_date else None
        
        apps_data.append({
            'id': app.id,
            'name': app.applicant.get_full_name() or app.applicant.username,
            'role': app.job.title,
            'match': 92, # Placeholder until ATS logic is hooked up
            'status': app.status,
            'date': "Recent", # You can replace with app.created_at.strftime() if you have a created date
            'interviewDate': int_date
        })
        
    # Send it to the template!
    context = {
        'applications_json': json.dumps(apps_data)
    }
    return render(request, 'users/talent.html', context)


import json
from django.utils import timezone
import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from jobs.models import Application  # <-- Verify this import matches your app!

@login_required
@require_POST
def update_application_status(request, app_id):
    """API endpoint for recruiters to update application statuses."""
    if not getattr(request.user, 'is_recruiter', False):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Fetch the exact application
        application = Application.objects.get(id=app_id)
        application.status = new_status
        
        # If scheduling an interview, auto-set the date for 3 days from now
        if new_status == 'scheduled':
            application.interview_date = timezone.now() + datetime.timedelta(days=3)
            
        application.save()
        return JsonResponse({'success': True, 'message': 'Status updated'})
        
    except Application.DoesNotExist:
        return JsonResponse({'error': 'Application not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

from jobs.models import JobListing # <-- Check that this matches your actual model name!

@login_required
def post_job_view(request):
    """Handles rendering the post job form and saving new jobs to the DB."""
    if not getattr(request.user, 'is_recruiter', False):
        return redirect('dashboard')
        
    if request.method == 'POST':
        
        JobListing.objects.create(
            title=request.POST.get('title'),
            company_name=request.POST.get('company_name'),
            
            # Map the HTML 'location' input to your model's 'work_mode' field
            work_mode=request.POST.get('location'), 
            
            # Map the HTML 'job_type' input to your model's 'employment_type' field
            employment_type=request.POST.get('job_type'), 
            
            # Pass the description
            description=request.POST.get('description'),
            
            # Since your model requires a 'company_type' but our HTML form didn't ask for it, 
            # we will set a default here so the database doesn't crash!
            company_type="Technology" 
        )
        return redirect('dashboard')
        
    # Notice this points to the 'users' folder now!
    return render(request, 'users/post_jobs.html')