from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class Skill(models.Model):
    """Skills required for job and will have many to many relationship with Job model"""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
    
    
class Job(models.Model):
    """Job posted by employer."""
    position = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # ManyToManyField: A job can require multiple skills, and a skill can be required by multiple jobs
    requirements = models.ManyToManyField(Skill, blank=True)
    employer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    
    class Meta:
        get_latest_by = 'created_at'
        ordering = ['-created_at']
    
    def num_applications(self):
        return self.applications.count()
    
    def __str__(self):
        return f"{self.position} (Posted: {self.created_at})"


class Application(models.Model):
    """Refers to the application sent by candidate."""
    # ForeignKey: Each application belongs to one job
    # related_name='applications': Enables Job.objects.applications.all() 
    # on_delete=CASCADE: If job is deleted, applications are also deleted
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.candidate.username} applied to {self.job.position}"

    class Meta:
        ordering = ['-applied_at']
        constraints = [
            models.UniqueConstraint(
                fields=['job', 'candidate'],
                name='unique_application',
            )
        ]



class CompanyProfile(models.Model):
    """Description of company"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True)
    