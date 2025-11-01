from rest_framework import serializers
from .models import User
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    """Serializers User inputs during login, registration."""
    class Meta:
        model = User
        fields = ['email','password','role','company','resume','username']
        read_only_fields = ['username','email','role']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
            'resume':{'required':False, 'allow_null':True},
            'company':{'required':False, 'allow_null':True},
            
        }
        
    def create(self,validated_data):
        """Ensures that django stores hashed password."""
        password = validated_data.pop('password',None)
        user = User(**validated_data)
        if password:
                user.set_password(password)
        user.save()
        return user
        
    def validate(self, attrs):
        """Checks if the correct fields are provided."""
        role = attrs.get('role')
        resume = attrs.get('resume')
        company = attrs.get('company')
        
        if role == User.RoleChoice.CAN and not resume:
            raise serializers.ValidationError({"resume": "Candidates must upload a resume."})
        if role == User.RoleChoice.EMP and not company:
            raise serializers.ValidationError({"company": "Employers must provide a company name."})

        return attrs
    
    def update(self,instance, validated_data):
        """Updates the user data partially or fully."""
        role = validated_data.get('role')
        resume = validated_data.get('resume')
        company = validated_data.get('company')
        
        if role!= instance.role:
            if role == User.RoleChoice.CAN:
                if not resume:
                    raise ValidationError({"resume":"Candidates must upload a resume."})
                instance.company = None
                instance.resume = resume
                
            elif role == User.RoleChoice.EMP:
                if not company:
                    raise ValidationError({"company":"Employer must provide the name of the company."})
                instance.resume = None
                instance.company = company
            instance.role = role
        else:
            if 'resume' in validated_data:
                instance.resume = resume
            if 'company' in validated_data:
                instance.company = company
        if 'username' in validated_data:
            instance.username = validated_data['username']
            
        instance.save()
        return instance
            