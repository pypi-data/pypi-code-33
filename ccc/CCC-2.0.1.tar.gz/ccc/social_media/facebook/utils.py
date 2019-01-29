from urllib.parse import quote

from django.urls import NoReverseMatch, reverse


def reverse_or_fail_silently(url_name, kwargs=None, query_params=None):
    """If the query params is not a dictionary, it fails silently"""
    if query_params is None and not isinstance(query_params, dict):
        query_params = dict()
    try:
        url = reverse(url_name, kwargs=kwargs)
    except NoReverseMatch:
        url = url_name
    return url + '?' + dict_to_url_args(query_params)


def dict_to_url_args(args_dict, encode_params=False):
    url_args = ''
    i = 0
    for key, value in args_dict.items():
        key = str(key)
        value = str(value)
        if encode_params:
            # If the encoding is enabled, then encode the URL parameters
            value = quote(value)
        if isinstance(value, list):
            url_args += key + '=' + ','.join(value)
        else:
            url_args += key + '=' + value
        if i < len(args_dict.keys()) - 1:
            url_args += '&'
        i += 1
    return url_args


def add_query_param_to_url(url, query_param_dict, encode_params=False):
    if bool(query_param_dict):
        if '?' in url:
            return url + '&' + dict_to_url_args(query_param_dict, encode_params)
        else:
            return url + '?' + dict_to_url_args(query_param_dict, encode_params)
    return url
