from django.contrib import admin

from .models import LdapGroup, LdapPerson


#
# Declare admin models
#

class LdapGroupAdmin(admin.ModelAdmin):
    exclude = ['dn', 'objectClass']
    list_display = ['cn', 'description', ]


class LdapPersonAdmin(admin.ModelAdmin):
    exclude = ['dn', 'objectClass']
    list_display = ['uid', 'mail', 'description', ]


#
# Register admin models
#

admin.site.register(LdapGroup, LdapGroupAdmin)
admin.site.register(LdapPerson, LdapPersonAdmin)
