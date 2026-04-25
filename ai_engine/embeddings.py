import chromadb
from chromadb.utils import embedding_functions

# 1. Initialize Persistent Storage
# This creates a hidden folder to save your vectors locally. 
# They will survive even if you restart the Django development server.
chroma_client = chromadb.PersistentClient(path="./.chroma_db_data")

# 2. Define the Embedding Model
# We explicitly tell Chroma to use the Hugging Face model you downloaded
embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 3. Create Vector Collections (Think of these as tables in SQL)
job_collection = chroma_client.get_or_create_collection(
    name="job_listings", 
    embedding_function=embedding_model
)

resume_collection = chroma_client.get_or_create_collection(
    name="resumes", 
    embedding_function=embedding_model
)

def store_job_listing(job_id, job_description, metadata):
    """
    Takes a new job listing from Hasaan's backend and stores its vector.
    """
    job_collection.upsert(
        documents=[job_description], # The raw text to embed
        metadatas=[metadata],        # e.g., {"title": "Backend Dev", "location": "Islamabad"}
        ids=[str(job_id)]            # Must be a string
    )
    return True

def store_resume(user_id, parsed_resume_text):
    """
    Takes the cleaned PDF text from your nlp_pipeline and stores it.
    """
    resume_collection.upsert(
        documents=[parsed_resume_text],
        ids=[f"user_{user_id}"]
    )
    return True

def get_semantic_job_matches(parsed_resume_text, n_results=5):
    """
    The core AI feature: Finds the top matching jobs for a given resume.
    Returns the Job IDs and the similarity distances.
    """
    results = job_collection.query(
        query_texts=[parsed_resume_text],
        n_results=n_results
    )
    
    # Chroma returns a dictionary with 'ids', 'distances', and 'documents'
    return results