from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import JobListing, Application
from django.views.decorators.http import require_POST

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
@require_POST
def apply_for_job(request, job_id):
    """API endpoint to handle job applications from Lumina/Explore page."""
    job = get_object_or_404(JobListing, id=job_id)
    
    # Check if THIS specific user has already applied for THIS specific job
    already_applied = Application.objects.filter(
        applicant=request.user, 
        job=job
    ).exists()
    
    if already_applied:
        return JsonResponse({
            'success': False, 
            'message': 'You have already applied for this position.'
        }, status=400)
    
    # Create the application
    Application.objects.create(
        applicant=request.user,
        job=job,
        status='pending'
    )
    
    return JsonResponse({'success': True})

@login_required
def my_applications_view(request):
    """Fetches all applications for the current user and renders the tracking dashboard."""
    # select_related('job') optimizes the database query since we need the job title/company
    applications = Application.objects.filter(applicant=request.user).select_related('job').order_by('-applied_at')
    
    return render(request, 'jobs/my_applications.html', {'applications': applications})

