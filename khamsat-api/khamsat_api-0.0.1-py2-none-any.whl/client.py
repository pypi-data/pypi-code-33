# coding: utf-8

import requests,re, uuid, \
	time, string, random

# disable ssl warning
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

from random_useragent.random_useragent import Randomize; r_agent = Randomize()

from .http import MultipartFormDataEncoder

class Client:

	uagent = r_agent.random_agent('smartphone','android')
	def __init__(self, **kwargs):
		self.timeout = kwargs.pop('timeout', 10)
		self.email = kwargs.pop('email', None)
		self.password = kwargs.pop('password', None)
		self.user_agent = kwargs.pop('user_agent', self.uagent)

		self.token = None
		self.login_token = None

		proxy = kwargs.pop('proxy', None)
		proxies = dict(
			http='{https!s}://{proxy!s}'.format(**{'https': 'https', 'proxy': proxy}),
			https='{https!s}://{proxy!s}'.format(**{'https': 'https', 'proxy': proxy})
		)	if proxy else None

		self.session = requests.Session()
		# set proxy!
		if proxies:
			self.session.proxies.update(proxies)

	@property
	def cookies(self):
		return self.session.cookies

	def _extract_token(self, headers=False):
		token = self.cookies.get('token', None)
		if not token and response:
			mobj = re.findall(
				'token=(.*?);', headers['Set-Cookie'], re.DOTALL
			)
			if mobj:
				token = mobj[0]
		return token

	def _extract_csrf_token(self, data):
		if data:
			mobj = re.findall(
				'name=\'token\' value=\'(.*?)\'', data, re.DOTALL
			)
			if mobj:
				return mobj[0]
		return None

	@staticmethod
	def read_response(response, isjson=False):
		if isjson:
			res = response.json()
		else:
			res = response.text.encode('utf-8')
		return res

	def make_request(self, url, json_or_params='', headers=None, method=None, allow_redirects=False, data=None):
		if not headers:
			headers = {
				'user-agent': self.user_agent,
				'accept': 'application/json',
				'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
				'accept-encoding': 'gzip, deflate, br',
				'content-type': 'application/json; charset=UTF-8',
				'content-length': '0',
				'x-locale': 'ar'
			}

		if method=='GET':
			req = self.session.get(
				url,
				headers=headers,
				params=json_or_params,
				verify=False,
				allow_redirects=allow_redirects,
				timeout=self.timeout
			)
		else:
			if not data:
				req = self.session.post(
					url,
					json=json_or_params,
					headers=headers,
					verify=False,
					allow_redirects=allow_redirects,
					timeout=self.timeout
				)
			else:
				req = self.session.post(
					url,
					data=data,
					headers=headers,
					verify=False,
					allow_redirects=allow_redirects,
					timeout=self.timeout
				)

		return req

	def login(self):
		login_token, headers = self.prepare_login()
		if login_token:
			endpoint = 'https://khamsat.com/login'

			params = {
				't': login_token
			}

			login_kh_mk = self.make_request(
				endpoint,
				headers=headers,
				json_or_params=params,
				method='GET',
				allow_redirects=True
			)

			if login_kh_mk:
				return True
		return False

	def prepare_login(self):
		endpoint = 'https://accounts.hsoub.com/api/login'
		params = dict(
			user = dict(
				email = self.email,
				password = self.password
			)
		)

		headers = {
			'user-agent': self.user_agent,
			'accept': 'application/json',
			'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
			'accept-encoding': 'gzip, deflate, br',
			'content-type': 'application/json; charset=UTF-8',
			'content-length': '0',
			'origin': 'https://accounts.hsoub.com',
			'referer': 'https://accounts.hsoub.com/login?next=/',
			'x-locale': 'ar',
			'x-ui-version': '4b7870a1-1f93-45eb-a52f-843dbef658cb'
		}

		login_mk = self.make_request(
			endpoint,
			json_or_params=params,
			headers=headers,
			method='POST',
			allow_redirects=True
		)

		if login_mk:
			self.token = self._extract_token(login_mk.headers)
			endpoint = 'https://accounts.hsoub.com/api/account'
			headers['authorization'] = 'Bearer %s' % self.token
			del headers['origin']

			account_mk = self.make_request(
				endpoint,
				headers=headers,
				method='GET',
				allow_redirects=True
			)

			if account_mk:
				account_rs = self.read_response(account_mk, True)
				self.login_token = account_rs.get('login_token', None)
				if self.login_token:
					return (self.login_token, headers)
		return (None, headers)

	def account_stats(self):
		endpoint = 'https://khamsat.com/ajax/account_stats'
		get_stats = self.make_request(
			endpoint,
			method='GET',
			allow_redirects=False
		)
		if get_stats:
			return self.read_response(get_stats, True)
		return None

	def send_message(self, msg_id, content):
		endpoint = 'https://khamsat.com/message/{msg_id:s}'.format(msg_id=msg_id)

		go_to_message = self.make_request(
			endpoint,
			method='GET',
			allow_redirects=False
		)
		if go_to_message:
			csrf_token = self._extract_csrf_token(self.read_response(go_to_message, False))
			if csrf_token:
				boundary = '----WebKitFormBoundary{}'.format(
					''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)))

				fields = [
					('content', content),
					('token', csrf_token),
					('last_id', ''),
				]
				files = []
				content_type, body = MultipartFormDataEncoder(boundary=boundary).encode(
					fields, files
				)
				headers = {
					'user-agent': self.user_agent,
					'accept': '*/*',
					'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
					'accept-encoding': 'gzip, deflate, br',
					'content-type': content_type,
					'content-length': str(len(body)),
					'origin': 'https://khamsat.com',
					'referer': endpoint,
					'x-requested-with': 'XMLHttpRequest'
				}

				message_mk = self.make_request(
					endpoint,
					headers=headers,
					method='POST',
					allow_redirects=True,
					data=body
				)

				if message_mk:
					return True
		return False
