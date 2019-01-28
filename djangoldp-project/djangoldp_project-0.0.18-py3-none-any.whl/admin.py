from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import Project, Member, Customer

admin.site.register(Project, GuardedModelAdmin)
admin.site.register(Member)
admin.site.register(Customer)
