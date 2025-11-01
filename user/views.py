from django.shortcuts import render
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner

User = get_user_model()


class UserManagementView(APIView):
    """Manages registration, login, and logout endpoint and jwt token authentication. """
    
    def get(self,request):
        """returns user info."""
        permission_classes = [IsOwner]
        user = request.user
        self.check_object_permissions(request,user)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def post(self,request):
        """creates a new user. """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message':'User created successfully.'},
                status=status.HTTP_201_CREATED
            ) 
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request):
        """updates user info."""
        permission_classes = [IsOwner]
        user = request.user
        self.check_object_permissions(request,user)
        serializer = UserSerializer(user,data=request.data, partial= True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status= status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        """deletes an user."""
        user = request.user
        self.check_object_permissions(request, user)
        if user:
            user.delete()
            return Response("Sucessfully deleted user!")    
        return Response(status=status.HTTP_404_NOT_FOUND)