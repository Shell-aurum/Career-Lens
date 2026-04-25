import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Resume, ATSReport
from .nlp_pipeline import extract_text_from_pdf, calculate_ats_score
from .embeddings import store_resume, get_semantic_job_matches
from .rag_chatbot import generate_rag_response
# Assuming Hasaan built a JobListing model in the jobs app
# from jobs.models import JobListing 

@login_required
@require_POST
def process_uploaded_resume(request):
    """
    Hasaan: Route the frontend PDF upload form here.
    This view extracts the text, saves the Django Resume model, 
    and stores the vector in ChromaDB.
    """
    pdf_file = request.FILES.get('resume_pdf')
    
    if not pdf_file:
        return JsonResponse({'error': 'No file provided.'}, status=400)

    try:
        # 1. Arsum's AI Pipeline: Extract text
        parsed_text = extract_text_from_pdf(pdf_file)
        if not parsed_text:
            return JsonResponse({'error': 'Could not read PDF.'}, status=422)

        # 2. Hasaan's DB Logic: Save to SQL
        resume = Resume.objects.create(
            user=request.user,
            file_path=pdf_file,
            parsed_text=parsed_text
        )

        # 3. Arsum's AI Pipeline: Store vector for semantic search
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
    """
    Hasaan: Call this when a user clicks 'Test ATS Score' on a specific job.
    Expects JSON payload with 'resume_id' and 'job_id'.
    """
    try:
        data = json.loads(request.body)
        resume_id = data.get('resume_id')
        job_id = data.get('job_id') # Use this to fetch the job description from DB
        
        # NOTE FOR HASAAN: Fetch the resume and job objects here. 
        # Example: 
        resume = Resume.objects.get(id=resume_id, user=request.user)
        # job = JobListing.objects.get(id=job_id)
        
        # Placeholder for the actual job description text
        job_description = "Placeholder job description from Hasaan's DB"

        # 1. Arsum's AI Pipeline: Calculate Score
        score, missing_skills = calculate_ats_score(resume.parsed_text, job_description)

        # 2. Hasaan's DB Logic: Save the report
        report = ATSReport.objects.create(
            resume=resume,
            job_id=job_id,
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
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def recommend_jobs(request):
    """
    Hasaan: Call this to populate the user's dashboard feed.
    """
    try:
        # Get the user's most recent parsed resume
        latest_resume = Resume.objects.filter(user=request.user).last()
        if not latest_resume:
            return JsonResponse({'error': 'Please upload a resume first.'}, status=400)

        # 1. Arsum's AI Pipeline: Query ChromaDB
        # Returns a dictionary with matched job_ids and distances
        matches = get_semantic_job_matches(latest_resume.parsed_text, n_results=5)

        # NOTE FOR HASAAN: Take matches['ids'][0], query your JobListing SQL table, 
        # and serialize the full job data (title, salary, etc.) to send to Saad.

        return JsonResponse({
            'matched_job_ids': matches['ids'][0],
            'distances': matches['distances'][0]
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def ask_rag_chatbot(request):
    """
    Hasaan: Route the premium user chat UI here.
    Expects JSON payload with 'query', 'resume_id', and 'job_id'.
    """
    try:
        data = json.loads(request.body)
        user_query = data.get('query')
        
        # NOTE FOR HASAAN: Fetch the context objects
        resume = Resume.objects.get(id=data.get('resume_id'))
        report = ATSReport.objects.filter(resume=resume, job_id=data.get('job_id')).last()
        # job = JobListing.objects.get(id=data.get('job_id'))
        
        job_desc = "Placeholder job description from Hasaan's DB"
        missing_skills = report.missing_skills if report else []

        # 1. Arsum's AI Pipeline: Generate LLM response
        bot_reply = generate_rag_response(
            user_query=user_query,
            parsed_resume=resume.parsed_text,
            job_description=job_desc,
            ats_missing_skills=missing_skills
        )

        return JsonResponse({'reply': bot_reply}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)