import os
from ai_engine.nlp_pipeline import extract_text_from_pdf, calculate_ats_score
from ai_engine.embeddings import store_resume, store_job_listing, get_semantic_job_matches

# --- 1. CONFIGURATION ---
RESUME_FILE = "Resume.pdf" 

# A realistic mock job description tailored to a technical internship
MOCK_JOB_DESCRIPTION = """
Technical Intern - Machine Learning & System Design
We are seeking a highly motivated data science student to join our summer engineering program. 
The ideal candidate will have a strong foundation in Data Structures, memory management, and C++ programming. 
Experience with building custom linked lists or AVL trees is highly desired. 
Additionally, knowledge of AI automation, Docker, and deploying NLP pipelines will set you apart. 
You must have a solid grasp of linear algebra and probability theory.
"""

def run_diagnostics():
    print("🚀 Starting Career Lens AI Core Diagnostics...\n")
    
    # --- 2. TEST PDF PARSING ---
    print(f"📄 Testing PDF Extraction for: {RESUME_FILE}")
    if not os.path.exists(RESUME_FILE):
        print(f"❌ ERROR: Could not find {RESUME_FILE} in the root directory.")
        return

    with open(RESUME_FILE, "rb") as file:
        parsed_text = extract_text_from_pdf(file)
        
    if not parsed_text:
        print("❌ ERROR: PDF parsing failed or returned empty text.")
        return
        
    print("✅ PDF Parsed Successfully!")
    print(f"📊 Word Count: {len(parsed_text.split())}")
    print("-" * 40)

    # --- 3. TEST ATS SCORING ---
    print("🧮 Testing ATS Evaluation Module...")
    ats_score, missing_skills = calculate_ats_score(parsed_text, MOCK_JOB_DESCRIPTION)
    
    print(f"🎯 Final ATS Score: {ats_score}/100")
    if missing_skills:
        print(f"⚠️ Missing Keywords Detected: {', '.join(missing_skills)}")
    else:
        print("🌟 Perfect Keyword Match!")
    print("-" * 40)

    # --- 4. TEST VECTOR EMBEDDINGS (CHROMADB) ---
    print("🧠 Testing Semantic Search (ChromaDB)...")
    
    # Store the Mock Job
    store_job_listing(
        job_id="test_job_001", 
        job_description=MOCK_JOB_DESCRIPTION, 
        metadata={"title": "Technical Intern", "company": "Mock Corp"}
    )
    print("✅ Mock Job Vector Stored in ChromaDB")
    
    # Store Your Resume
    store_resume(user_id="arsum_99", parsed_resume_text=parsed_text)
    print("✅ Resume Vector Stored in ChromaDB")
    
    # Run Semantic Match
    results = get_semantic_job_matches(parsed_text, n_results=1)
    
    print("\n🔍 Semantic Search Results:")
    print(f"Matched Job ID: {results['ids'][0][0]}")
    # Distance: Lower is better (closer to 0 means higher similarity)
    print(f"Vector Distance: {results['distances'][0][0]:.4f}")
    print("\n🎉 All AI modules executed successfully!")

if __name__ == "__main__":
    run_diagnostics()