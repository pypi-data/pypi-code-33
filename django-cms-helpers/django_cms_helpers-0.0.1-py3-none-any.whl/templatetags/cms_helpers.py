from cms.models import Page
from cms.utils.moderator import use_draft
from django import template
from django.core.exceptions import ObjectDoesNotExist


register = template.Library()


@register.simple_tag(takes_context=True)
def page_titleextension(context, page_id, extension):
    try:
        page = Page.objects.get(pk=page_id)
        if 'request' in context and use_draft(context['request']):
            page = page.get_draft_object()
        else:
            page = page.get_public_object()
    except NameError:
        raise ImportError(
            'django-cms is required when using page_titleextension tag')
    except Page.DoesNotExist:
        return None

    if not page:
        return None

    try:
        return getattr(page.get_title_obj(), extension)
    except ObjectDoesNotExist:
        return None
