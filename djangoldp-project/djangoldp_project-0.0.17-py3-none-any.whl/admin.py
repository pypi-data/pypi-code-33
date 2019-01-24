from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import Project, Job, Customer

admin.site.register(Project, GuardedModelAdmin)
admin.site.register(Job)
admin.site.register(Customer)
