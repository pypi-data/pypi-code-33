from . import settings


def sso_cookie_domain(request):
    return {
        "sso_cookie_domain": settings.SSO_COOKIE_DOMAIN
    }
