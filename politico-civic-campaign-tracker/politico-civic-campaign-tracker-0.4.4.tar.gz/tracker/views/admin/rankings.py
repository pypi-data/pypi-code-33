from tracker.conf import settings as app_settings
from tracker.utils.auth import secure
from django.views.generic import TemplateView


@secure
class RankingsAdmin(TemplateView):
    template_name = "tracker/admin/rankings.html"
    name = "Rankings admin"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["secret"] = app_settings.SECRET_KEY

        if self.kwargs.get("pk") and self.kwargs.get("pk") != "new":
            context["id"] = self.kwargs.get("pk")

        return context
