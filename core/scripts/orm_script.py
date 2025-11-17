from django.contrib.auth import get_user_model
from core.models import Job,Application,Skill
from django.db.models import Q,Case,When,F,Exists,Count



def run():
    # review of old orm queries 
    
    #TASK1: print all the available jobs with more than 3 applicants
    # job = Job.objects.prefetch_related('applications').annotate(
    #     job_count = Count('applications__id')
    # ).values('description','job_count')
    # print([(j['job_count'],j['description']) for j in job])
    
    
    #print all the applications
    # applications = Application.objects.all().count()
    # print(applications)
    
    
    #print job correspond to applications 

    # app = Application.objects.annotate(
    #     job_requirements=F('job__requirements'),
    #     job_description=F('job__description'),
    # ).values('job_requirements', 'job_description')

    # for a in app:
    #     print((a['job_description'],a['job_requirements']))

    pass