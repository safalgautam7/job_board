from .serializers import JobCreateSerializer,ApplicationSerializer,JobListSerializer
from .models import Job,Application,Skill,CompanyProfile
from rest_framework.response import Response
from rest_framework import status,viewsets
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class JobView(viewsets.ModelViewSet):
    """Manages CRUD operation for job model."""
    queryset = Job.objects.all()
    
    #default serializer class 
    serializer_class = JobCreateSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        return self.serializer_class
    
    def destroy(self, request, *args, **kwargs):
        job = self.get_object()
        user = request.user
        
        if user.role != User.RoleChoice.EMP:
            return Response(
                {"detail": "Only employers can delete jobs."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if job.employer != user:
            return Response(
                {'detail':'You are not authorized to delete this job.'},
                status = status.HTTP_403_FORBIDDEN
            )
        if job.is_active:
            return Response({"detail": "Cannot delete an active job."}, status= status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)
    
    
class ApplicationView(viewsets.ModelViewSet):
    """Allows candidate to create, read, update and delete their application."""