import os
import google.generativeai as genai

# Securely load your API key from environment variables
# Make sure to add GEMINI_API_KEY to your .env file
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_rag_response(user_query, parsed_resume, job_description, ats_missing_skills):
    """
    Retrieves the contextual data and generates an LLM response tailored 
    to the user's specific resume and target job.
    """
    
    # 1. Construct the System Prompt with Strict Context
    prompt = f"""
    You are an expert AI Career Coach embedded in the CareerLens platform.
    Your goal is to answer the user's question using ONLY the provided context.
    Be candid, highly analytical, and constructive.

    --- SYSTEM CONTEXT ---
    Candidate's Extracted Resume:
    {parsed_resume}

    Target Job Description:
    {job_description}

    ATS System Flagged Missing Skills:
    {', '.join(ats_missing_skills) if ats_missing_skills else 'None detected.'}
    ----------------------

    User Question: {user_query}
    
    Instructions:
    - If the user asks how to improve, reference specific missing skills.
    - If the user asks if they are a good fit, compare their resume experience to the job description.
    - If the question is completely unrelated to tech, jobs, or resumes, politely decline to answer.
    """
    
    # 2. Call the Model
    try:
        # Using flash for high-speed, low-latency generation (crucial for chat UI)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        print(f"RAG Engine Error: {e}")
        return "I'm currently experiencing a connection issue. Please try your question again in a moment."