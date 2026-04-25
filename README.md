# Career Lens

Career Lens is an AI-driven job discovery and resume intelligence platform. It utilizes a Django Client-Server architecture to provide job seekers with semantic job matching, Applicant Tracking System (ATS) evaluation, and a Retrieval-Augmented Generation (RAG) career coach.

## System Architecture

The platform leverages a hybrid database approach and a dedicated machine learning microservice within the Django monolith:
* **Frontend:** HTML, CSS, JavaScript, Tailwind CSS (UI/UX)
* **Backend:** Django (MVT Pattern), SQLite/PostgreSQL (Relational Data)
* **AI Engine:**
  * `PyPDF2` for document parsing and text extraction.
  * `sentence-transformers` (`all-MiniLM-L6-v2`) for local vector embeddings.
  * `ChromaDB` for high-speed semantic similarity search.
  * `Google Gemini API` for context-aware RAG chatbot responses.

## Local Development Setup

### 1. Clone and Configure Environment
Ensure you have Python installed, then set up the virtual environment:
```bash
git clone <your-repository-url>
cd CareerLens
python -m venv .venv

# Activate the environment (Windows)
.\.venv\Scripts\activate
# Activate the environment (Mac/Linux)
source .venv/bin/activate
```

### 2. Install Dependencies
Install the required web and AI libraries:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your Gemini API key for the RAG chatbot:
```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Run Diagnostics & Server
To verify the AI core is functioning correctly before booting the server:
```bash
python test_ai_core.py
python manage.py runserver
```

## The Development Team
Developed for Fundamentals of Software Engineering (Iteration 3):
* **Arsum Ullah** - Project Lead, Requirements Engineering & Core AI Pipeline
* **Muhammad Hasaan** - Backend Architecture & Database Integrations
* **Saad Hassan** - Frontend Implementation, UI/UX & Quality Assurance