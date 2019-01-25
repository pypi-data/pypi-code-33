from django.core.cache import cache


def expire_page(path):
    cache.clear()
    return
