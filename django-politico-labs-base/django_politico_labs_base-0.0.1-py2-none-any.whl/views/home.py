from django.views.generic import TemplateView

from base.utils.auth import secure


@secure
class Home(TemplateView):
    template_name = "base/home.html"
