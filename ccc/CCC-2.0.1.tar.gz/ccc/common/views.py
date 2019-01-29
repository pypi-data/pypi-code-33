from django.views.generic import View

from ccc.campaigns.utils.shortcut import shorten_url
from ccc.common.mixins import AjaxableResponseMixin, LoginRequiredAjaxMixin


class ShortURLView(LoginRequiredAjaxMixin, AjaxableResponseMixin, View):
    """Get Short url from given url"""

    def get(self, request, *args, **kwargs):
        """"""
        long_url = request.GET.get('long_url')
        try:
            if long_url:
                return self.render_to_json_response({'short_url': shorten_url(long_url)}, status=200)
        except Exception as ex:
            return self.render_to_json_response({'short_url': str(ex)}, status=200)
        return self.render_to_json_response({'short_url': 'Unable to create short url'}, status=400)
