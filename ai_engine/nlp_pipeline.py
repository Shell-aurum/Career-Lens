import PyPDF2
import re

def extract_text_from_pdf(pdf_file_obj):
    """
    Takes an uploaded PDF file object and extracts all text.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "
        return clean_text(text)
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return None

def clean_text(raw_text):
    """
    Removes excess whitespace, special characters, and normalizes text.
    """
    # Remove excessive newlines and tabs
    text = re.sub(r'\s+', ' ', raw_text)
    # Convert to lowercase for uniform embedding generation
    text = text.lower().strip()
    return text

def extract_keywords(text):
    """
    A lightweight function to extract potential skills/keywords from text.
    Removes common stop words and returns a set of unique words.
    """
    # Standard stop words to ignore
    stop_words = {
        'and', 'the', 'is', 'in', 'to', 'with', 'for', 'of', 'a', 'on', 'at',
        'our', 'ours', 'we', 'you', 'your', 'will', 'be', 'an', 'as', 'are',
        'have', 'has', 'had', 'from', 'by', 'that', 'this', 'these', 'those',
        'it', 'its', 'seeking', 'set', 'ideal', 'candidate', 'highly', 'strong',
        'knowledge', 'addition', 'additionally', 'must', 'solid', 'grasp', 'program',
        'apart', 'join', 'foundation', 'experience', 'desired', 'motivated', 'out', 'up',
        'we', 'are', 'who', 'what', 'where', 'when', 'why', 'how', 'which', 'their', 'or',
        'building', 'summer'
    }
    
    # Extract words, convert to lowercase
    words = re.findall(r'\b[a-z0-9\+\#\.]{2,}\b', text.lower())
    
    # Return unique keywords excluding stop words
    return set(word for word in words if word not in stop_words)


def calculate_ats_score(parsed_resume, job_description):
    """
    Calculates an ATS score (0-100) based on keyword overlap and length.
    """
    if not parsed_resume or not job_description:
        return 0, []

    resume_keywords = extract_keywords(parsed_resume)
    job_keywords = extract_keywords(job_description)
    
    # Find matching skills
    matched_keywords = resume_keywords.intersection(job_keywords)
    missing_keywords = list(job_keywords.difference(resume_keywords))
    
    # 1. Keyword Match Score (Weight: 70%)
    if len(job_keywords) > 0:
        keyword_score = (len(matched_keywords) / len(job_keywords)) * 70
    else:
        keyword_score = 0
        
    # 2. Structural/Length Score (Weight: 30%)
    # Assuming a healthy resume text has a decent word count
    resume_word_count = len(parsed_resume.split())
    if 200 <= resume_word_count <= 800:
        structure_score = 30
    elif resume_word_count > 800:
        structure_score = 20 # Penalize for being too long
    else:
        structure_score = 15 # Penalize for being too brief

    # Calculate final score
    final_score = int(keyword_score + structure_score)
    
    # Cap at 100 just in case
    final_score = min(final_score, 100)
    
    return final_score, missing_keywords[:5] # Return score and top 5 missing skills