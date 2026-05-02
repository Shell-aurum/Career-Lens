import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Resume, ATSReport
from .nlp_pipeline import extract_text_from_pdf, calculate_ats_score
from .embeddings import store_resume, get_semantic_job_matches
from .rag_chatbot import generate_rag_response
from jobs.models import JobListing 
from django.shortcuts import render, redirect



@login_required
@require_POST
def process_uploaded_resume(request):
   
    pdf_file = request.FILES.get('resume_pdf')
    
    if not pdf_file:
        return JsonResponse({'error': 'No file provided.'}, status=400)

    try:
        # AI Pipeline: Extract text
        parsed_text = extract_text_from_pdf(pdf_file)
        if not parsed_text:
            return JsonResponse({'error': 'Could not read PDF.'}, status=422)

        # DB Logic: Save to SQL
        resume = Resume.objects.create(
            user=request.user,
            file_path=pdf_file,
            parsed_text=parsed_text
        )

        # AI Pipeline: Store vector for semantic search
        store_resume(user_id=request.user.id, parsed_resume_text=parsed_text)

        return JsonResponse({
            'message': 'Resume processed successfully.',
            'resume_id': resume.id,
            'word_count': len(parsed_text.split())
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@login_required
@require_POST
def generate_ats_evaluation(request):
    try:
        data = json.loads(request.body)
        resume_id = data.get('resume_id')
        job_id = data.get('job_id') 
        
        resume = Resume.objects.get(id=resume_id, user=request.user)
        
        # Query the real SQL database
        job = JobListing.objects.get(id=job_id)
        job_description = job.description 

        # AI Pipeline: Calculate Score
        score, missing_skills = calculate_ats_score(resume.parsed_text, job_description)

        report = ATSReport.objects.create(
            resume=resume,
            job_id=job.id, # Store the actual ID
            final_score=score,
            missing_skills=missing_skills
        )

        return JsonResponse({
            'report_id': report.id,
            'score': score,
            'missing_skills': missing_skills
        }, status=200)

    except Resume.DoesNotExist:
        return JsonResponse({'error': 'Resume not found.'}, status=404)
    except JobListing.DoesNotExist:
        return JsonResponse({'error': 'Selected job no longer exists.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@login_required
def recommend_jobs(request):
    try:
        latest_resume = Resume.objects.filter(user=request.user).last()
        if not latest_resume:
            return JsonResponse({'error': 'Please upload a resume first.'}, status=400)

        matches = get_semantic_job_matches(latest_resume.parsed_text, n_results=5)

        return JsonResponse({
            'matched_job_ids': matches['ids'][0],
            'distances': matches['distances'][0]
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@login_required
def chatbot_interface(request):
    """Renders the Premium Chatbot UI for BOTH Seekers and Recruiters."""
    
    # Check if the user has a resume that ACTUALLY contains parsed text
    has_resume = Resume.objects.filter(user=request.user).exclude(parsed_text__isnull=True).exclude(parsed_text="").exists()
    
    return render(request, 'ai_engine/chatbot.html', {'has_resume': has_resume})

@login_required
@require_POST
def ask_rag_chatbot(request):
    """Handles async messages and routes logic based on user role."""
    try:
        data = json.loads(request.body)
        user_query = data.get('query')

        if not user_query:
            return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

        is_recruiter = getattr(request.user, 'is_recruiter', False)

        if is_recruiter:
            # 1. RECRUITER LOGIC: Pass only the query and role
            bot_reply = generate_rag_response(
                user_query=user_query,
                role="recruiter"
            )
        else:
            # 2. JOB SEEKER LOGIC: Fetch context
            resume = Resume.objects.filter(user=request.user).last()
            parsed_resume = resume.parsed_text if resume else "The user hasn't uploaded a resume yet."

            latest_report = ATSReport.objects.filter(resume=resume).last() if resume else None
            
            if latest_report:
                job = JobListing.objects.get(id=latest_report.job_id)
                job_desc = job.description
                missing_skills = latest_report.missing_skills
            else:
                job_desc = "No specific job targeted yet."
                missing_skills = []

            bot_reply = generate_rag_response(
                user_query=user_query,
                role="job_seeker",
                parsed_resume=parsed_resume,
                job_description=job_desc,
                ats_missing_skills=missing_skills
            )

        return JsonResponse({'reply': bot_reply}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@login_required
def talent_pool_view(request):
    """Renders the ATS Talent Pool for recruiters."""
    # Security check: Kick out anyone who isn't a recruiter
    if not getattr(request.user, 'is_recruiter', False):
        return redirect('dashboard')
        
    return render(request, 'users/talent.html')