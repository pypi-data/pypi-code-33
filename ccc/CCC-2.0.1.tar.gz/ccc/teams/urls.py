from django.conf.urls import url

from ccc.teams.views import (Real, accept_invite, create_team, delete_member,
                             delete_team, InviteMemberFormView,
                             TeamDetailView, TeamsListView, OtherTeamsListView)

app_name = 'teams'

urlpatterns = [
    url(r'^$', TeamsListView.as_view(), name='teams'),
    url(r'^create/$', create_team, name='create_team'),
    url(r'^real/$', Real, name='real'),
    url(r'^(?P<team_id>\d+)/$', TeamDetailView.as_view(), name='team_detail'),
    url(r'^(?P<team_id>\d+)/invite/$', InviteMemberFormView.as_view(), name='invite_member'),
    url(r'^invite/(?P<token>\w+)/$', accept_invite, name='accept_invite'),
    url(r'^(?P<team_id>\d+)/delete/$', delete_team, name='delete-team'),
    url(r'^my-invited-teams/$', OtherTeamsListView.as_view(), name='other_teams'),
    url(r'^delete-from-team/(?P<mbr_id>\d+)/$', delete_member, name='delete-team-mbr'),
]
