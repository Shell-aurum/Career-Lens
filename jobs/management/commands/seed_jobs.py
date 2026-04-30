from django.core.management.base import BaseCommand
from jobs.models import JobListing

class Command(BaseCommand):
    help = 'Wipes the JobListing table and seeds it with dummy jobs for development.'

    def handle(self, *args, **kwargs):
        # 1. Clear existing data to avoid duplicates on re-runs
        self.stdout.write("Deleting old jobs...")
        JobListing.objects.all().delete()

        # 2. Define the dummy data
        dummy_jobs = [
            {
                "title": "Software Engineer", "company_name": "Google", "company_type": "IT",
                "salary_min": 120000, "salary_max": 180000, "employment_type": "Full-time", 
                "work_mode": "On-site", "description": "Develop scalable backend systems using Python, Django, and Docker."
            },
            {
                "title": "Embedded Systems Engineer", "company_name": "Tesla", "company_type": "Engineering",
                "salary_min": 90000, "salary_max": 140000, "employment_type": "Full-time", 
                "work_mode": "On-site", "description": "Work on C++ firmware for automotive control systems and logical operations."
            },
            {
                "title": "AI Researcher", "company_name": "OpenAI", "company_type": "AI",
                "salary_min": 150000, "salary_max": 220000, "employment_type": "Full-time", 
                "work_mode": "Remote", "description": "Research and develop advanced AI models using Retrieval-Augmented Generation (RAG) and LLMs."
            },
            {
                "title": "Cloud Engineer", "company_name": "Amazon", "company_type": "IT",
                "salary_min": 110000, "salary_max": 160000, "employment_type": "Full-time", 
                "work_mode": "Remote", "description": "Manage AWS infrastructure and automated CI/CD deployments."
            },
            {
                "title": "Frontend Developer", "company_name": "Microsoft", "company_type": "Development",
                "salary_min": 80000, "salary_max": 120000, "employment_type": "Full-time", 
                "work_mode": "Hybrid", "description": "Build responsive user interfaces using React, JavaScript, and Tailwind CSS."
            },
            {
                "title": "Data Scientist", "company_name": "Meta", "company_type": "AI",
                "salary_min": 130000, "salary_max": 190000, "employment_type": "Full-time", 
                "work_mode": "Remote", "description": "Analyze large datasets for insights using Machine Learning, Linear Algebra, and Calculus."
            },
            {
                "title": "Project Manager", "company_name": "IBM", "company_type": "Management",
                "salary_min": 70000, "salary_max": 110000, "employment_type": "Full-time", 
                "work_mode": "On-site", "description": "Lead cross-functional engineering teams utilizing Agile methodologies."
            },
            {
                "title": "Deep Learning Engineer", "company_name": "NVIDIA", "company_type": "AI",
                "salary_min": 140000, "salary_max": 210000, "employment_type": "Full-time", 
                "work_mode": "On-site", "description": "Optimize neural networks for GPUs, focusing on probability theory and complex variables."
            },
            {
                "title": "Backend Systems Engineer", "company_name": "LinkedIn", "company_type": "Development",
                "salary_min": 125000, "salary_max": 175000, "employment_type": "Full-time", 
                "work_mode": "Remote", "description": "Scale our real-time messaging architecture using custom data structures, AVL trees, and hashing."
            },
            {
                "title": "Automation Solutions Developer", "company_name": "Freelance Client", "company_type": "Development",
                "salary_min": 60000, "salary_max": 90000, "employment_type": "Contract", 
                "work_mode": "Remote", "description": "Build automated social media pipelines using n8n, AI agents, and webhooks."
            }
        ]

        # 3. Insert into the database
        self.stdout.write("Seeding new jobs...")
        for job_data in dummy_jobs:
            JobListing.objects.create(**job_data)

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(dummy_jobs)} jobs into the database!'))