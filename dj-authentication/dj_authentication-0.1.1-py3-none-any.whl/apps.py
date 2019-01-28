from django.apps import AppConfig
from django.http import HttpRequest

try:
	from rest_framework.request import Request
except ImportError:
	# If DRF is not used, we don't need to patch it.
	class Request:
		pass


class DjAuthenticationConfig(AppConfig):
	name = 'dj_authentication'

	def ready(self):
		from .request_user import request_user, drf_request_user
		from .request_http_auth import request_http_auth
		HttpRequest.user = request_user
		HttpRequest.http_auth = request_http_auth
		Request.user = drf_request_user
