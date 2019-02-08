from logging import getLogger
from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.urls import reverse
from .client import client
from .errors import IllegalStateError
import string
import random


logger = getLogger(__name__)


class Start(View):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        chars = string.ascii_letters + string.digits
        stored_nonce = ''.join([random.choice(chars) for i in range(32)])
        stored_state = ''.join([random.choice(chars) for i in range(32)])
        request.session['stored_nonce'] = stored_nonce
        request.session['stored_state'] = stored_state
        client.prepare(request)
        redirect_uri = \
            request.build_absolute_uri(reverse('kantanoidc:callback'))
        return HttpResponseRedirect(
            client.build_starturl(redirect_uri, stored_nonce, stored_state)
        )


class Callback(View):

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        state = request.GET.get('state')
        if state != request.session['stored_state']:
            raise IllegalStateError('state <> stored_state')
        code = request.GET.get('code')
        stored_nonce = request.session['stored_nonce']
        sub = client.get_sub(code, stored_nonce)
        logger.debug('sub=%s', sub)
        user = User.objects.get_by_natural_key(sub)
        login(request, user)
        nexturl = client.build_nexturl(request)
        return HttpResponseRedirect(nexturl)
