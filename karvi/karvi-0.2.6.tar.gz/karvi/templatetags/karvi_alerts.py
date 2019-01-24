from django import template

register = template.Library()


@register.inclusion_tag("karvi/addons/alerts.html")
def karvi_alert(message, type=None, title=None, dismissible=False):
    if not type:
        type = ""
    return {"message": message, "type": type, "title": title, "dismissible": dismissible}
