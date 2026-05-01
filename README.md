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

## Project Structure

```text
CareerLens/
│
├── career_lens_core/          # The main Django project configuration folder
│   ├── settings.py            # Global settings, DB configs, installed apps
│   ├── urls.py                # Main URL router
│   └── wsgi.py / asgi.py      # Server entry points
│
├── users/                     # Django App: Authentication & Profiles
│   ├── models.py              # User, JobSeeker, Recruiter models
│   ├── views.py               # Login, registration, dashboard logic
│   └── forms.py               # Form validation for signups
│
├── jobs/                      # Django App: Market Aggregation & Listings
│   ├── models.py              # JobListing, Application models
│   ├── views.py               # Search, filter, and apply logic
│   └── utils.py               # API integration scripts (Adzuna/JSearch)
│
├── ai_engine/                 # Django App / Module: The Brains
│   ├── models.py              # Resume, ATSReport models
│   ├── nlp_pipeline.py        # PDF text extraction and skill parsing
│   ├── embeddings.py          # Sentence transformer logic & Vector DB connection
│   ├── rag_chatbot.py         # LLM context retrieval and generation
│   └── views.py               # Endpoints for ATS scoring and semantic search
│
├── templates/                 # Frontend: HTML structure
│   ├── base.html              # Main layout shell (navbars, footers)
│   ├── users/                 # Login, signup, user dashboard HTML
│   └── jobs/                  # Job feed, job detail, ATS report HTML
│
├── static/                    # Frontend: Assets
│   ├── css/                   # Stylesheets (Tailwind output goes here)
│   ├── js/                    # Client-side interactivity (upload loaders, chatbot UI)
│   └── images/                # Logos, icons exported from your Figma prototype
│
├── tests/                     # Test Suite (Preparing for Task 3)
│   ├── test_auth.py           # Unit tests for login/registration
│   ├── test_ai_pipeline.py    # Unit tests for PDF parsing and ATS scoring
│   └── test_bva.py            # Boundary Value Analysis tests
│
├── .gitignore                 # Exclude virtual environments, vector DB files, and API keys
├── requirements.txt           # Python dependencies (Django, transformers, PyPDF2, etc.)
└── README.md                  # Project overview and run instructions
```
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
GROQ_API_KEY= generate and use your own api key
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
