from base64 import b64decode

from django.conf import settings
from django.contrib.auth import authenticate


def get_user(request):
	params = dict(realm = settings.BASE_URL)

	credentials = request.http_auth('Basic', params)
	if credentials is not None:
		uname, passwd = b64decode(credentials.encode('ascii')).decode('utf-8').split(':')
		user = authenticate(request = request, username = uname, password = passwd)
		if user:
			return user


ClientSecretBasicAuth = get_user


def ClientSecretPostAuth(request):
	client_id = request.POST.get('client_id')
	client_secret = request.POST.get('client_secret')

	if client_id and client_secret:
		user = authenticate(request = request, username = client_id, password = client_secret)
		if user:
			return user
