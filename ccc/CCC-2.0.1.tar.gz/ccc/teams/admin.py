from django.contrib import admin

from ccc.teams.models import Team, TeamMember


class MemberAdmin(admin.ModelAdmin):
    list_display = ['phone', 'user']


admin.site.register(Team)
admin.site.register(TeamMember, MemberAdmin)
