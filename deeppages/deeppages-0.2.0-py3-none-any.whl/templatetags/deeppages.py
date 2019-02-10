from django import template
from deeppages.utils import get_page_by_slug

register = template.Library()


@register.simple_tag(takes_context=True)
def dp_include(context, slug):
    page = get_page_by_slug(slug, context=context)
    return page
