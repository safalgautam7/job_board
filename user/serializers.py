from rest_framework import serializers
from .models import User
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    """Serializes User inputs during login, registration."""
    
    class Meta:
        model = User
        fields = ['email', 'password', 'role', 'company', 'resume', 'username']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
            'resume': {'required': False, 'allow_null': True},
            'company': {'required': False, 'allow_null': True},
            'username': {'required': False}, 
        }
        
    def create(self, validated_data):
        """Ensures that django stores hashed password and handles username generation."""
        password = validated_data.pop('password', None)
        
        # If username not provided, it will be generated in the manager
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
        
    def validate(self, attrs):
        """Checks if the correct fields are provided."""
        role = attrs.get('role')
        resume = attrs.get('resume')
        company = attrs.get('company')
        
        # Only validate during creation (not update)
        if self.instance is None:  # This is for create operation
            if role == User.RoleChoice.CAN and not resume:
                raise serializers.ValidationError({"resume": "Candidates must upload a resume."})
            if role == User.RoleChoice.EMP and not company:
                raise serializers.ValidationError({"company": "Employers must provide a company name."})

        return attrs
    
    def update(self, instance, validated_data):
        """Updates the user data partially or fully."""
        password = validated_data.pop('password', None)
        role = validated_data.get('role', instance.role)
        resume = validated_data.get('resume')
        company = validated_data.get('company')
        
        # Handle role change validation
        if role != instance.role:
            if role == User.RoleChoice.CAN and not resume:
                raise serializers.ValidationError({"resume": "Candidates must upload a resume when changing role."})
            elif role == User.RoleChoice.EMP and not company:
                raise serializers.ValidationError({"company": "Employers must provide a company name when changing role."})
            
            if role == User.RoleChoice.CAN:
                instance.company = None
            elif role == User.RoleChoice.EMP:
                instance.resume = None
        
        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        """Add any additional login validation if needed."""
        return attrs