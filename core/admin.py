from django.contrib import admin
from .models import Skill, Job, Application, CompanyProfile

admin.site.register(Skill)
admin.site.register(Job)
admin.site.register(Application)
admin.site.register(CompanyProfile)

