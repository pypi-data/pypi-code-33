from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import CustomerInvoice
from .models import FreelanceInvoice
from .models import Batch
from .models import Task

admin.site.register(CustomerInvoice)
admin.site.register(FreelanceInvoice)
admin.site.register(Batch)
admin.site.register(Task)
