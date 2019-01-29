from tracker.conf import settings as app_settings
from tracker.utils.auth import secure
from django.views.generic import TemplateView


@secure
class RankingSetsAdmin(TemplateView):
    template_name = "tracker/admin/ranking-sets.html"
    name = "Ranking sets admin"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["secret"] = app_settings.SECRET_KEY
        return context
