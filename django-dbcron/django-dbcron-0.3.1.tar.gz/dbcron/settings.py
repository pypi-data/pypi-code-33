from django.conf import settings


def get_setting(name, *default):
    full_name = 'DBCRON_%s' % name
    value = getattr(settings, full_name, *default)
    return value


MAX_WORKERS = get_setting('MAX_WORKERS', 8)
