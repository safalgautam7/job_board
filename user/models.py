import random
import string
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.core.exceptions import ValidationError


def generate_username_from_email(email):
    """Generate a username from the first 3 chars of the email (before @)"""
    base = email.split('@')[0][:3].lower()
    base = ''.join(ch for ch in base if ch.isalnum()) 
    username = base

    from .models import User  # avoid circular import

    # ensure uniqueness
    while User.objects.filter(username=username).exists():
        suffix = ''.join(random.choices(string.digits, k=3))
        username = f"{base}{suffix}"

    return username


class UserProfileManager(BaseUserManager):
    """Manager for user profiles"""
    def create_user(self,email,username,role,resume= None, company = None, password = None,):
        if not email:
            raise ValidationError("User must enter email")
        email = self.normalize_email(email)
        
        if not username:
            username = generate_username_from_email()
            
        user = self.model(email =email, username = username, role = role)
        
        #Attach company or resume depedning on role
        if role == user.RoleChoice.EMP and company:
            user.company = company
        elif role == user.RoleChoice.CAN and resume:
            user.resume = resume
        
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self,email, username, password = None):
        """Create and return a new superuser."""
        user = self.create_user(
            email = email,
            username = username,
            role = User.RoleChoice.EMP,
            password = password
        ) 
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)
        return user   


class User(AbstractBaseUser,PermissionsMixin):
    """Database model for users in the system"""
    class RoleChoice(models.TextChoices):
        EMP = 'Employer'
        CAN = 'Candidate'
        
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    role = models.CharField(max_length=10,choices=RoleChoice)
    resume = models.FileField(upload_to='uploads/',blank=True,null=True)
    company = models.CharField(max_length=255, null=True,blank=True)
    
    objects = UserProfileManager() 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']
    
    def __str__(self):
        return f"{self.username} with role as {self.role}"
    
