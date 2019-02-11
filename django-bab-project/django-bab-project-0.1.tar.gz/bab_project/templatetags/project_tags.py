from django import template
register = template.Library()

from ..models import Category, Customer

@register.inclusion_tag('bab_project/widgets/categories.html')
def widget_categories():
    categories = Category.objects.all()

    return {'categories': categories}


@register.inclusion_tag('bab_project/widgets/partners_modals.html')
def partners_modals():
    active_partners = [partner for partner in Customer.objects.all() if partner.projects.count() ]
    return {
        'active_partners': active_partners
    }
