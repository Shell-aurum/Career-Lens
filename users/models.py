from django.db import models
from django.contrib.auth.models import AbstractUser

# The core User table handling emails and passwords securely
class User(AbstractUser):
    # Django handles name, email, and password automatically
    is_job_seeker = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)

# The Job Seeker table
class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    subscription_status = models.CharField(max_length=50, default='free')

    def _str_(self):
        return f"Job Seeker: {self.user.username}"

# The Recruiter table
class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    is_premium = models.BooleanField(default=False)

    def _str_(self):
        return f"Recruiter: {self.company_name}"