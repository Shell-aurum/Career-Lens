from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import JobListing, Application

@login_required
def api_get_all_jobs(request):
    try:
        jobs = JobListing.objects.all().order_by('-posted_date')
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                # ... keep your existing fields ...
                'id': job.id,
                'company': job.company_name,
                'type': job.company_type,
                'title': job.title,
                'salaryMin': job.salary_min or "----",
                'salaryMax': job.salary_max or "----",
                'empType': job.employment_type,
                'mode': job.work_mode,
                'desc': job.description,
                'postedDate': job.posted_date.strftime('%Y-%m-%d'),
                # UPDATE THIS LINE: Route to our new Django view
                'link': f"/jobs/{job.id}/apply/" 
            })
        return JsonResponse({'jobs': jobs_data}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def apply_job_view(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)

    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        
        # Check if the user already applied
        if Application.objects.filter(job=job, applicant=request.user).exists():
            # In a real app, you'd show this error on the UI. 
            # For now, redirect back to dashboard.
            print("User already applied to this job.") 
            return redirect('dashboard')

        # Save to database
        Application.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=cover_letter
        )
        
        # Redirect to dashboard upon success
        return redirect('dashboard')

    return render(request, 'jobs/apply_job.html', {'job': job})

@login_required
def my_applications_view(request):
    """Fetches all applications for the current user and renders the tracking dashboard."""
    # select_related('job') optimizes the database query since we need the job title/company
    applications = Application.objects.filter(applicant=request.user).select_related('job').order_by('-applied_at')
    
    return render(request, 'jobs/my_applications.html', {'applications': applications})

@login_required
def talent_pool_view(request):
    """Renders the ATS Talent Pool for recruiters."""
    # Security check: Kick out anyone who isn't a recruiter
    if not getattr(request.user, 'is_recruiter', False):
        return redirect('dashboard')
        
    return render(request, 'users/talent.html')

