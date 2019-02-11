from django import template
from ..models import Category, Note

register = template.Library()


@register.inclusion_tag('bab_cms/widgets/categories.html')
def widget_categories():
    categories = Category.objects.all()

    return {'categories': categories }


@register.inclusion_tag('bab_cms/widgets/summary.html')
def widget_summary(article):
    return {
        'summary': article.get_root().get_descendants(include_self=True)
    }


@register.inclusion_tag('bab_cms/widgets/note.html')
def widget_note():
    return { 'note': Note.objects.filter(display=True).last()}
