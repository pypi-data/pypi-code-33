# -*- coding: utf-8 -*-
import re
from django import template
from django.urls import reverse, NoReverseMatch, resolve, Resolver404

register = template.Library()

@register.simple_tag(takes_context=True)
def navactive(request, url, exact=1, use_resolver=1):
    """
    Returns ``active`` if the given URL is in the url path, otherwise ''.
    Usage::
        {% load libs_tags %}
        ...
        <li class="{% navactive request "/news/" exact=1 %}">
    :param request: A request instance.
    :param url: A string representing a part of the URL that needs to exist
      in order for this method to return ``True``.
    :param exact: If ``1`` then the parameter ``url`` must be equal to
      ``request.path``, otherwise the parameter ``url`` can just be a part of
      ``request.path``.
    :use_resolver: If ``0`` we will not try to compare ``url`` with existing
      view names but we will only compare it with ``request.path``.
    """
    if use_resolver:
        try:
            if url == resolve(request.path).url_name:
                # Checks the url pattern in case a view_name is posted
                return 'active'
            elif url == request.path:
                # Workaround to catch URLs with more than one part, which don't
                # raise a Resolver404 (e.g. '/index/info/')
                match = request.path
            else:
                return ''
        except Resolver404:
            # Indicates, that a simple url string is used (e.g. '/index/')
            match = request.path
    else:
        match = request.path

    if exact and url == match:
        return 'active'
    elif not exact and url in request.path:
        return 'active'
    return ''

@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    try:
        pattern = '^' + reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname
    path = context['request'].path
    if re.search(pattern, path):
        return 'active'
    return ''
    

@register.simple_tag(takes_context=True)
def active_url(context, urls, css=None):
    """
    Highlight menu item based on url tag.
    
    Returns a css class if ``request.path`` is in given ``url``.
    
    :param url:
        Django url to be reversed.

    :param css:
        Css class to be returned for highlighting. Return active if none set.

    """
    request = context['request']
    if request.get_full_path in (reverse(url) for url in urls.split()):
        return css if css else 'active'
    return ''

@register.simple_tag(takes_context=True)
def active_path(context, pattern, css=None):
    """
    Highlight menu item based on path.
    
    Returns a css class if ``request.path`` is in given ``pattern``.
    
    :param pattern:
        Regex url pattern.

    :param css:
        Css class to be returned for highlighting. Return active if none set.

    """
    request = context['request']
    #pattern = "^" + pattern + "$"
    if re.search(pattern, request.path):
        return css if css else 'active'
    return ''
