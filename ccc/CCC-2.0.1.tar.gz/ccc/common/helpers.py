from django.contrib.sites.models import Site
from django.urls import reverse


def get_full_url(url_name, *args, **kwargs):
    relative_url = reverse(url_name, args=args, kwargs=kwargs)
    return 'https://%s%s' % (Site.objects.get_current().domain, relative_url)
