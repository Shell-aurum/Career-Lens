from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User, JobSeeker, Recruiter

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

from django.contrib.auth import authenticate, login

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


from django.contrib.auth import logout # Make sure this is imported at the top!

# ... your other views ...

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home') # Sends them back to the login page
    
from django.contrib.auth.decorators import login_required

# Ensure only logged-in users can see the job board
@login_required
def explore_view(request):
    return render(request, 'users/explore.html')

@login_required
def analyse_resume_view(request):
    # This view just displays the upload page. 
    # Later, we will point the HTML form to POST directly to the ai_engine.
    return render(request, 'users/analyse_resume.html')

