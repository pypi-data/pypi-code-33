# Import models
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView

from ccc.packages.decorators import check_user_subscription
from ccc.packages.models import TwilioNumber
from ccc.teams.forms import FormInviteMember
from ccc.teams.models import Team, TeamMember


@login_required
@check_user_subscription
def create_team(request):
    """
    Create new Team
    """

    if request.method == "POST":
        name = request.POST.get("name", None)
        description = request.POST.get("description", None)
        phone = request.POST.get("phone", None)

        if name:
            team = Team.objects.create(name=name, description=description, creator=request.user)
            if phone:
                phones = TwilioNumber.objects.filter(id=phone)
                if phones:
                    phone = phones[0]
                    team.phone = phone
                    team.save()
                    phone.in_use = True
                    phone.save()
    return HttpResponseRedirect(reverse('srm:teams:teams'))


@login_required
@check_user_subscription
def delete_team(request, team_id):
    """
    delete  Team
    """

    team = get_object_or_404(Team, id=team_id)
    if team.phone:
        phone = team.phone
        phone.in_use = False
        phone.save()
    team.delete()

    return HttpResponseRedirect(reverse('srm:teams:teams'))


@login_required
@check_user_subscription
def delete_member(request, mbr_id):
    """
    delete  Team Member
    """
    member = get_object_or_404(TeamMember, id=mbr_id)
    team = member.team.id
    member.delete()

    return HttpResponseRedirect(reverse('srm:teams:team_detail', args=[team]))


class InviteMemberFormView(FormView):
    """Send an individual invitation to joining to a specific Team"""
    form_class = FormInviteMember
    template_name = 'crm/teams/forms/invite_member.html'

    def dispatch(self, request, *args, **kwargs):
        return super(InviteMemberFormView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        team = get_object_or_404(Team, id=self.kwargs['team_id'])
        form.add_member(team)
        return self.get_success_url()

    def form_invalid(self, form):
        messages.error(self.request, "Name, email & phone are required to invite team members.")
        return HttpResponseRedirect(
            reverse("srm:teams:team_detail", kwargs={"team_id": self.kwargs['team_id']})
        )

    def get_success_url(self):
        return HttpResponseRedirect(reverse("srm:teams:team_detail",
                                            kwargs={'team_id': self.kwargs['team_id']}))


class TeamsListView(ListView):
    """Listing all teams created"""
    template_name = 'crm/teams/my_teams.html'
    queryset = Team.objects.all()
    ordering = '-date_created'
    context_object_name = 'pag_teams'
    paginate_by = 100

    @method_decorator(login_required)
    @method_decorator(check_user_subscription)
    def dispatch(self, request, *args, **kwargs):
        return super(TeamsListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(TeamsListView, self).get_queryset()
        return qs.filter(creator=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TeamsListView, self).get_context_data(**kwargs)
        context['numbers'] = TwilioNumber.objects.filter(
            user=self.request.user,
            is_redirected=False,
            in_use=False
        )
        return context


class OtherTeamsListView(ListView):
    """Listing the teams that user is invited to..."""
    template_name = 'crm/teams/invited_teams.html'
    queryset = Team.objects.all()
    ordering = '-date_created'
    context_object_name = 'pag_teams'
    paginate_by = 100

    @method_decorator(login_required)
    @method_decorator(check_user_subscription)
    def dispatch(self, request, *args, **kwargs):
        return super(OtherTeamsListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        teams = TeamMember.objects.values_list('id', flat=True).filter(user=self.request.user)
        qs = super(OtherTeamsListView, self).get_queryset()
        return qs.filter(id__in=teams)


@csrf_exempt
def Real(request):
    if request.method == 'POST':

        print('Hello')
        import datetime

        return HttpResponse(json.dumps({'time': str(datetime.datetime.now())}))
    else:
        return render(request, 'real.html')


class TeamDetailView(TemplateView):
    template_name = 'crm/teams/team_detail.html'

    @method_decorator(login_required)
    @method_decorator(check_user_subscription)
    def dispatch(self, request, *args, **kwargs):
        return super(TeamDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        team = get_object_or_404(Team, id=self.kwargs['team_id'])
        context['team'] = team
        context['members'] = TeamMember.objects.filter(team=team.id)
        context['form_invite_member'] = FormInviteMember
        return context


def accept_invite(request, token):
    member = get_object_or_404(TeamMember, token=token)
    return render(request, 'crm/teams/complete_invite.html', locals())
