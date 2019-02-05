from django.conf import settings
from django.shortcuts import render


def home(request):
    render_data = {
        "username": request.user.get_username(),
        "site_title": settings.SITE_TITLE,
        "site_byline": settings.SITE_BYLINE,
        "site_provider": settings.SITE_PROVIDER,
        "site_provider_link": settings.SITE_PROVIDER_LINK,
    }

    return render(request, 'purist/home.html', render_data)


def jslicense(request):
    render_data = {
        "site_title": settings.SITE_TITLE,
    }

    return render(request, 'purist/jslicense.html', render_data)
