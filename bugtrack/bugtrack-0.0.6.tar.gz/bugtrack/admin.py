from bugtrack.models import BugStatus, Category, Priority, Severity
from django.contrib import admin


class BugStatusAdmin(admin.ModelAdmin):
    pass



class CategoryAdmin(admin.ModelAdmin):
    pass



class PriorityAdmin(admin.ModelAdmin):
    pass



class SeverityAdmin(admin.ModelAdmin):
    pass


admin.site.register(BugStatus, BugStatusAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Priority, PriorityAdmin)
admin.site.register(Severity, SeverityAdmin)
