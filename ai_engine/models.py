from django.db import models
from django.conf import settings

class Resume(models.Model):
    # Links to Hasaan's custom User model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    file_path = models.FileField(upload_to='resumes/')
    parsed_text = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume for User ID: {self.user_id}"

class ATSReport(models.Model):
    # Links the report strictly to the uploaded resume
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='ats_reports')
    
    # Stores the ID of the job they tested against (from the jobs app or ChromaDB)
    job_id = models.CharField(max_length=255) 
    
    # The scores generated from your nlp_pipeline.py
    final_score = models.IntegerField(default=0)
    
    # Django's JSONField is perfect for storing your Python list of missing keywords
    missing_skills = models.JSONField(default=list) 
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ATS Report {self.id} | Score: {self.final_score}"