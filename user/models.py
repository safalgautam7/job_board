import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.core.exceptions import ValidationError
from django.utils.text import slugify


def generate_username_from_email(email):
    """Generate a unique username from email."""
    local_part = email.split('@')[0]
    base_username = slugify(local_part)
    
    if not base_username:
        base_username = "user"
    
    unique_id = uuid.uuid4().hex[:8]
    unique_username = f"{base_username}_{unique_id}"
    
    return unique_username


class UserProfileManager(BaseUserManager):
    def create_user(self, email, username=None, role=None, resume=None, company=None, password=None, **extra_fields):
        if not email:
            raise ValidationError("User must have an email address")
        
        #checks if email already exists
        if self.model.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email already exists")

        #email normalization 
        email = self.normalize_email(email)
        email = email.lower()

        if not username:
            username = generate_username_from_email(email)

        User = self.model
        user = User(
            email=email, 
            username=username, 
            role=role,
            **extra_fields
        )

        #roles should be either CAN or EMP
        valid_roles = [choice[0] for choice in User.RoleChoice.choices]
        if role and role not in valid_roles:
            raise ValueError(f"Invalid role: {role}. Must be one of {valid_roles}")

        #No role checking for super_user
        if not extra_fields.get('is_superuser', False):
            if role == User.RoleChoice.EMP and not company:
                raise ValidationError("Employers must provide a company name")
            
            if role == User.RoleChoice.CAN and not resume:
                raise ValidationError("Candidates must provide a resume")

        if role == User.RoleChoice.EMP and company:
            user.company = company
        elif role == User.RoleChoice.CAN and resume:
            user.resume = resume

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        User = self.model
        role = extra_fields.pop('role', User.RoleChoice.EMP)

        extra_fields['is_superuser'] = True
        
        user = self.create_user(
            email=email,
            username=username or generate_username_from_email(email),
            role=role,
            password=password,
            **extra_fields
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    
class User(AbstractBaseUser, PermissionsMixin):
    """Database model for users."""

    class RoleChoice(models.TextChoices):
        EMP = 'EMP', 'Employer'  
        CAN = 'CAN', 'Candidate'

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    role = models.CharField(max_length=3, choices=RoleChoice.choices) 
    resume = models.FileField(upload_to='uploads/', blank=True, null=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return f"{self.username} ({self.role})"