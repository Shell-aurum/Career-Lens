import os
from groq import Groq
from dotenv import load_dotenv

# Force load the .env file
load_dotenv()

# Initialize the Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_rag_response(user_query, role="job_seeker", parsed_resume=None, job_description=None, ats_missing_skills=None):
    """
    Dynamically generates an LLM response using Groq's blazing fast Llama 3 model.
    """
    
    if role == "recruiter":
        # --- RECRUITER MODE ---
        system_context = """
        You are an expert AI Hiring Assistant embedded in the CareerLens platform.
        Your goal is to help recruiters draft compelling job descriptions, formulate technical interview questions, and identify key skills for tech roles.
        Be professional, concise, and highly knowledgeable about the tech industry.
        """
    else:
        # --- JOB SEEKER MODE ---
        system_context = f"""
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
        """
    
    try:
        # Call the Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_context
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,        # Low temp keeps the coach focused and factual
            max_tokens=500,
        )
        
        # Extract the text response
        bot_reply = chat_completion.choices[0].message.content
        return bot_reply
        
    except Exception as e:
        error_msg = str(e)
        print(f"Groq API Error: {error_msg}")
        return f"Groq API Error: {error_msg}"