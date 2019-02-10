import logging

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template import Template, Context
from django.template.loader import get_template


#from mycms.models import Paths, Pages
#from mycms.pageview.base import get_pageview

from mycms.models import  CMSPaths
from mycms.models import CMSEntries

register = template.Library()

logger = logging.getLogger("mycms.templatetags")


@register.inclusion_tag('mycms/templatetags/dropdown_menu.html')
def dropdown_menu(path):

    try:
        parent = CMSEntries.objects.get(path__path=path)
    except ObjectDoesNotExist as e:
        msg = "No CMSEntries to produce dropdown_menu for path: {}".format(path)
        logger.fatal(msg)
        parent = []
    return {"parent":parent}

@register.inclusion_tag('mycms/templatetags/full_menu.html')
def full_menu():
    """
    Used to get a full category tree starting from /cms/. 
    """
    
    try:
        parent = CMSEntries.objects.get(path__path="/")
    except ObjectDoesNotExist as e:
        msg = "No CMSEntries to produce full_menu from /. Perhaps / does not yet exist!!"
        logger.fatal(msg)
        parent = None
    return {"parent":parent}


@register.inclusion_tag('mycms/templatetags/mini_menu.html')
def mini_menu():
    try:
        parent = CMSEntries.objects.get(path__path="/")
    except ObjectDoesNotExist as e:
        msg = "No CMSEntries to produce full_menu from /. Perhaps / does not yet exist!!"
        logger.fatal(msg)
        parent = None
    return {"parent":parent}










