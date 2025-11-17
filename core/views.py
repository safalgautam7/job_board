from .serializers import JobCreateSerializer,ApplicationSerializer
from .models import Job,Application,Skill,CompanyProfile
from rest_framework.response import Response
from rest_framework import status,viewsets
from django.contrib.auth import get_user_model

User = get_user_model()

class JobView(viewsets.ModelViewSet):
    """Manages CRUD operation for job model."""
    queryset = Job.objects.all()