from django.urls import path
from django.conf import settings
from django.contrib import admin

def getup_middleware(get_response):
    # One-time configuration and initialization.

    if settings.getup_urls:
        urlconf = tuple(i for i in settings.getup_urls)

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if request.path.startswith('/admin'):
            request.urlconf = (path("admin/", admin.site.urls),)
            response = get_response(request)
            response["X-GETUP"] = "stand up!"
        elif urlconf:
            request.urlconf = urlconf
            response = get_response(request)
        else:
            response = get_response(request)
            
        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
