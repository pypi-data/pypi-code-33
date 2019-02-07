"""Singular API Client settings. Should not be modified
SINGULAR_URL: Default Sigular API URL, if none is provided when constructing Client
ENDPOINTS: Singular API endpoints to be called when invoking Client methods"""

SINGULAR_URL = 'https://paneasily.com/'
try:
    from django.conf import settings
    SINGULAR_URL = getattr(settings, 'SINGULAR', {}).get('URL', SINGULAR_URL)
except ImportError:
    pass

ENDPOINTS = {
    'example_method': {
        'url': 'example/',
        'method': 'POST'
    },
    'ping': {
        'url': 'api/ping/',
        'method': 'GET'
    }
}
