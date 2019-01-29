from django.views.generic import ListView

from ccc.common.mixins import LoginRequiredMixin
from ccc.tutorial.models import Video


class TutorialVideoList(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'crm/tutorials/tutorial.html'
