from rest_framework import serializers
from .models import Skill,Job,Application,CompanyProfile
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model

User = get_user_model()


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['name']
        

class JobListSerializer(serializers.ModelSerializer):
    """Lists jobs."""
    skills = SkillSerializer(many = True, read_only = True)
    fields = '__all__'
    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields


class JobCreateSerializer(serializers.ModelSerializer):
    """ creates and updates Job model."""
    skills = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True,
        write_only=True
    )
    
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['employer', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        skill_names = validated_data.pop('skills', [])
        user = self.context['request'].user
        
        if user.role != User.RoleChoice.EMP:
            raise ValidationError('Only employers can create jobs.')

        job = Job.objects.create(
            employer=user,
            **validated_data
        )
        

        skill_objects = []
        for skill_name in skill_names:
            skill, _ = Skill.objects.get_or_create(name=skill_name.strip())
            skill_objects.append(skill)
        
        job.requirements.set(skill_objects)
        return job
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        
        if user.role != User.RoleChoice.EMP:
            raise ValidationError('Only employers can update jobs.')
        
        if instance.employer != user:
            raise ValidationError('You are not authorized to perform the action!')
        
        skill_names = validated_data.pop('skills', None)
        

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skill_names is not None:
            skill_objects = []
            for skill_name in skill_names:
                skill, _ = Skill.objects.get_or_create(name=skill_name.strip())
                skill_objects.append(skill)
            instance.requirements.set(skill_objects)
        
        return instance
    

class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Application model."""
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['candidate', 'applied_at', 'updated_at']
        
    def validate_job(self, value):
        """Validate that the job is active before allowing applications."""
        if not value.is_active:
            raise serializers.ValidationError("Cannot apply to inactive jobs.")
        return value
        
    def create(self, validated_data):
        user = self.context['request'].user
        
        if user.role != User.RoleChoice.CAN:
            raise ValidationError('Only candidates can submit job applications.')
        
        job = validated_data['job']
        
        # Check if the user has already applied to this job
        if Application.objects.filter(job=job, candidate=user).exists():
            raise ValidationError("You have already applied to this job.")
        
        application = Application.objects.create(
            candidate=user,
            **validated_data
        )
        return application
    
    def update(self, instance, validated_data):
        user = self.context['request'].user

        if instance.candidate != user:
            raise ValidationError("You are not authorized to perform this action.")
        
        if user.role != User.RoleChoice.CAN:
            raise ValidationError("Only candidates can update their applications.")
        
        # prevents from changing the job after application is created
        if 'job' in validated_data and validated_data['job'] != instance.job:
            raise ValidationError("Cannot change the job for an existing application.")
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


