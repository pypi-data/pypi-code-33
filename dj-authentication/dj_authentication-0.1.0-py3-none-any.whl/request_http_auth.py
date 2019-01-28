from django.utils.cache import patch_vary_headers


def challenge_to_string(scheme, params):
	s = scheme
	for name, value in params.items():
		s += ' {}="{}"'.format(name, value.replace('\\', '\\\\').replace('"', '\\"'))
	return s


def request_http_auth(request, scheme, params):
	request.auth_challenges.append((scheme, params))

	header = request.META.get('HTTP_AUTHORIZATION')
	if not header:
		return None

	try:
		given_scheme, given_param = header.split(' ', 1)
	except:
		given_scheme, given_param = header, ''

	if given_scheme.lower() == scheme.lower():
		return given_param
	else:
		return None


class HTTPAuthMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		request.auth_challenges = []

		response = self.get_response(request)

		if request.auth_challenges:
			patch_vary_headers(response, ['Authorization'])
			for i, challenge in enumerate(request.auth_challenges):
				whatever = 'WWW-Authenticate' + str(i)
				response._headers[whatever] = ('WWW-Authenticate', challenge_to_string(*challenge))

		return response
