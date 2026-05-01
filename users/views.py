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