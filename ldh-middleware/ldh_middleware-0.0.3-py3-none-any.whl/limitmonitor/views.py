from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import render

from .models import Limit


@login_required
def userlimit(request):
    username = request.user.get_username()
    limits = Limit.objects.filter(user__username=username)

    # get flags for each limit
    has_limit = {}
    none_limit = True
    for limit in limits:
        label = limit.service_label().upper()
        has_limit[label] = limit.is_active

        if limit.is_active:
            none_limit = False

    has_limit["NONE"] = none_limit  # true if no limits are active

    render_data = {
        "DEBUG_CHANGE_PASSWORD": settings.DEBUG_CHANGE_PASSWORD,
        "username": username,
        "site_title": settings.SITE_TITLE,
        "site_byline": settings.SITE_BYLINE,
        "site_provider": settings.SITE_PROVIDER,
        "site_provider_link": settings.SITE_PROVIDER_LINK,
        "limits": limits,
        "has_limit": has_limit,
        "link_profile_ordered_dict": settings.LINK_PROFILE_ORDERED_DICT,
    }

    return render(request, 'limitmonitor/userlimit.html', render_data)


@login_required
def ovpn_userfile(request):
    user_identity = request.user.get_identity()
    filepath = settings.OVPN_FILEPATH.replace("{USER_IDENTITY}", user_identity)

    response = FileResponse(open(filepath, 'rb'), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="purist.ovpn"'
    return response
