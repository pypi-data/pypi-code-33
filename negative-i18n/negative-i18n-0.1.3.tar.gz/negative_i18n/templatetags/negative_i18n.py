from django.template import Library
from django.template.defaultfilters import stringfilter

from negative_i18n.trans_utils import translate_lazy


register = Library()


@register.filter(name='_')
@stringfilter
def translate_string(value):
    try:
        from threadlocals.threadlocals import get_current_request

        request = get_current_request()

        # negative-inline-editable plugin
        if request and request.session.get('editable'):
            if not hasattr(request, 'editable_strings'):
                request.editable_strings = set()

            request.editable_strings.add(value)

    except ImportError:
        pass

    return translate_lazy(value)

