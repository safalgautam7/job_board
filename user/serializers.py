from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializers User inputs during login, registration."""
    class Meta:
        model = User
        fields = ['email','password','role','copmany','resume']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
            'resume':{'required':False, 'allow_null':True},
            'company':{'required':False, 'allow_null':True},
        }
        
        def validate(self, attrs):
            pass