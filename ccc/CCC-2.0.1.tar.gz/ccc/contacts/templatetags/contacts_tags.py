from django import template

register = template.Library()


@register.filter
def na(data):
    """To display N/A"""
    if not data:
        return 'N/A'
    return data


@register.filter
def nodata(data):
    """To display N/A"""
    if not data:
        return ''
    return data


@register.filter
def sic(industries):
    divs = []
    for industry in industries:
        if industry.get('type') == 'SIC':
            divs.append("""<p>{}&nbsp;<span class="label label-primary">{}</span></p>""".format(industry.get('name'),
                                                                                                industry.get('code')))
    return ''.join(divs)


@register.filter
def keywords(keywords):
    if keywords:
        ' '.join(keywords)
