from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class JobListing(models.Model):
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    company_type = models.CharField(max_length=100, help_text="e.g., IT, AI, Engineering")
    employment_type = models.CharField(max_length=100, default="Full-time")
    work_mode = models.CharField(max_length=100, help_text="e.g., Remote, On-site, Hybrid")
    
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    
    description = models.TextField(help_text="The full job description for ATS analysis")
    posted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.company_name}"
    

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewing', 'Under Review'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('accepted', 'Offer Extended'),
    ]
    
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    interview_date = models.DateTimeField(null=True, blank=True)
    

    class Meta:
        # Prevent a user from applying to the same job twice
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.username} applied to {self.job.title}"