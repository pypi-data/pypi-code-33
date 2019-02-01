from rest_framework.compat import (INDENT_SEPARATORS, LONG_SEPARATORS, SHORT_SEPARATORS, )
from rest_framework.renderers import JSONRenderer
from rest_framework.utils import json
from django.utils import six


class StructuredJsonRenderer(JSONRenderer):
    """
    Decorator for standard response. Add structure response

    Need add in your settings:

    import universal_response_mobile_api as u_mobile_api

    'DEFAULT_RENDERER_CLASSES': (
            'u_mobile_api.StructuredJsonRenderer',
        ),
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        structured_data = {
            'success': True,
            'error': None,
            'message': '',
            'response': data,
        }

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS

        try:
            if data.get('error'):
                structured_data = data
        except AttributeError:
            pass

        ret = json.dumps(
            structured_data, cls=self.encoder_class,
            indent=indent, ensure_ascii=self.ensure_ascii,
            allow_nan=not self.strict, separators=separators
        )

        if isinstance(ret, six.text_type):
            ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
            return bytes(ret.encode('utf-8'))
        return ret
