from django.conf import settings
from django.template import Library
from django.urls import resolve, reverse
from django.utils.translation import activate, get_language

register = Library()


@register.simple_tag(takes_context=True)
def change_lang(context, lang=None, *args, **kwargs):
    """
    Get active page's url by a specified language
    Usage: {% change_lang 'en' %}
    """

    path = context['request'].path

    url = path

    if not lang:
        return url

    try:
        url_parts = resolve(path)

        cur_language = get_language()
        try:
            activate(lang)
            kwargs = url_parts.kwargs

            if 'urls' in context:
                for key, val in kwargs.items():

                    if key in context['urls']:
                        expr = context['urls'][key]
                        target, attr_expr = [x.strip() for x in expr.split('->')]

                        expr_formated = attr_expr.format(lang=lang)

                        if target not in context:
                            raise Exception('Error when parsing url expression for view  "{}", key'
                                            ' "{}": target is not in context: {}'.format(
                                url_parts.view_name, key, target
                            ))

                        try:
                            kwargs[key] = getattr(context[target], expr_formated)
                        except Exception as e:
                            raise Exception(
                                'Error when parsing url expression for view "{}", key "{}": {}'.format(
                                    url_parts.view_name, key, e
                                ))

            url = reverse(url_parts.view_name, kwargs=kwargs)
        finally:
            activate(cur_language)

        if settings.LANG_URLS and lang in settings.LANG_URLS:
            url = '{}{}'.format(settings.LANG_URLS[lang], url)

    except Exception as e:
        pass

    return url
