# ------------------------------------------------
#	Python Siesta
# Siesta is a REST client for python
#
#	Copyright (c) 2008 Rafael Xavier de Souza
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------
#
# Modified at Sep 20, 2017 by Hans Roh
#
# ------------------------------------------------

__version__ = "0.5.2"
__author__ = "Sebastian Castillo <castillobuiles@gmail.com>"
__contributors__ = []

import re
import time
import logging
import json
import requests
import base64
from urllib.parse import urlparse, urlencode
from .attrdict import AttrDict
import html2text
import io
import pprint

USER_AGENT = "Python-siesta/%s" % __version__

class Auth(object):
	def encode_params(self, base_url, method, params):
		raise NotImplementedError()

	def make_headers(self):
		pass


class APIKeyAuth(Auth):
	def __init__(self, api_key, auth_header_name="Authorization"):
		self.api_key = api_key
		self.auth_header_name = auth_header_name

	def encode_params(self):
		pass

	def make_headers(self):
		return {self.auth_header_name: self.api_key, }


class BasicAuth(Auth):
	def __init__(self, api_username, api_password, auth_header_name="Authorization"):
		self.api_username = api_username
		self.api_password = api_password
		self.auth_header_name = auth_header_name
		
	def encode_params(self):
		basic_token = base64.encodestring('' + str(self.api_username) + ':' + str(self.api_password))
		basic_token = basic_token.replace('\n', '')
		return basic_token
	
	def make_headers(self):
		token = self.encode_params()
		return {self.auth_header_name: 'Basic ' + token, }

class Response (object):
	def __init__ (self, resource, respnose):
		self.__response = respnose
		self.resource = resource
		self.data = AttrDict ()
		self.set_data (respnose)		
	
	def __getattr__ (self, attr):
		return getattr (self.__response, attr)
	
	def __str__ (self):
		if not isinstance (self.data, str):			
			s = io.StringIO()
			pprint.pprint(self.data, s)
			d = s.getvalue()		
		else:
			d = self.data	
		return "%d %s\n%s" % (self.__response.status_code, self.__response.reason, d)
		
	def set_data (self, resp):
		if not resp.text.strip ():
			self.data = None
		
		else:	
			ct = resp.headers.get ('content-type')
			if ct is None or ct.find ('text/html') == 0:
				h = html2text.HTML2Text()
				h.ignore_links = True
				text = h.handle(resp.text)
				self.data = text
					
			elif ct is None or ct.find ('text/') == 0:
				self.data = resp.text.strip ()
			else:
				data = resp.json ()
				if isinstance (data, dict):
					self.data.update (data)
				else:
					self.data = data

		if self.resource._reraise_http_error and not str(resp.status_code).startswith("2"):			
			raise AssertionError (self)
		

class Resource (object):
	ACCEPT = 'application/json'
	CONTENT_TYPE = 'application/json'
	
	def __init__(self, uri, api, logger, reraise_http_error = True, callback = None):
		self._api = api
		self._uri = uri
		self._logger = logger
		self._reraise_http_error = reraise_http_error
		self._callback = callback
		self._scheme, self._host, self._url = urlparse (self._api.base_url + self._uri) [:3]
		self._headers = {'User-Agent': USER_AGENT, "Accept": self.ACCEPT}
		
	def __getattr__(self, name):	
		key = self._uri + '/' + name
		return self.__class__ (uri=key, api=self._api, logger = self._logger, reraise_http_error = self._reraise_http_error, callback = self._callback)		

	def __call__(self, *ids):
		if not ids:
			return self		
		key = self._uri
		for id in ids:
			if key:
				key += '/' + str (id)
			else:
				key += str (id)	
		return Resource(uri=key, api=self._api, logger = self._logger, reraise_http_error = self._reraise_http_error, callback = self._callback)		
	
	def _request (self, method, data, headers, slash, **kwargs):
		if slash:
			self._url = self._url + "/"
		url = self._url		
		if len(kwargs) > 0:
			url = "%s?%s" % (url, urlencode(kwargs))
		headers = headers or {"Content-Type": self.CONTENT_TYPE}
		if self._callback:
			return self._callback (method, url, data, headers)
		return self._continue_request (method, url, data, headers)
	
	def get(self, _headers = None, **kwargs):
		return self._request ('GET', None, _headers, False, **kwargs)
	
	def delete(self, _headers = None, **kwargs):
		return self._request ('DELETE', None, _headers, False, **kwargs)
	
	def options(self, _headers = None, **kwargs):
		return self._request ('OPTIONS', None, _headers, False, **kwargs)	
				
	def post(self, data, _headers = None, **kwargs):
		return self._request ('POST', data, _headers, False, **kwargs)
	
	def put(self, data, _headers = None, **kwargs):
		return self._request ('PUT', data, _headers, False, **kwargs)
	
	# For slash ended endpoint
	def patch_(self, data, _headers = None, **kwargs):
		return self._request ('PATCH', data, _headers, False, **kwargs)

	def get_(self, _headers = None, **kwargs):
		return self._request ('GET', None, _headers, True, **kwargs)
	
	def delete_(self, _headers = None, **kwargs):
		return self._request ('DELETE', None, _headers, True, **kwargs)
	
	def options_(self, _headers = None, **kwargs):
		return self._request ('OPTIONS', None, _headers, True, **kwargs)	
				
	def post_(self, data, _headers = None, **kwargs):
		return self._request ('POST', data, _headers, True, **kwargs)
	
	def put_(self, data, _headers = None, **kwargs):
		return self._request ('PUT', data, _headers, True, **kwargs)
	
	def patch_(self, data, _headers = None, **kwargs):
		return self._request ('PATCH', data, _headers, True, **kwargs)

	def _continue_request(self, method, url, data, headers):
		if self._api.auth:
			headers.update(self._api.auth.make_headers())		
		if not 'User-Agent' in headers:
			headers['User-Agent'] = self._headers['User-Agent']
		if not 'Accept' in headers and 'Accept' in self._headers:
			headers['Accept'] = self._headers['Accept']
		
		url = "%s://%s%s" % (self._scheme, self._host, url)		
		if isinstance (data, dict):			
			data = json.dumps (data)
			
		func = getattr (self._api.session, method.lower ())
		if data is not None:
			if not isinstance (data, str):
				raise TypeError ("payload should be str or dic type")
			resp = func (url, data, headers = headers, timeout = self._api.REQ_TIMEOUT, verify = False)	
		else:
			resp = func (url, headers = headers, timeout = self._api.REQ_TIMEOUT, verify = False)
									
		return self._getresponse (resp)
		
	def _getresponse(self, resp):
		if resp.status_code == 202:
			status_url = resp.getheader('content-location')
			if not status_url:
				raise Exception('Empty content-location from server')

			status_uri = urlparse(status_url).path
			resource = Resource(uri=status_uri, api=self._api, logger = self._logger, reraise_http_error = self._reraise_http_error, callback = self._callback).get()
			retries = 0
			MAX_RETRIES = 3
			resp_status = resource.response.status_code
			
			while resp_status != 303 and retries < MAX_RETRIES:			
				retries += 1
				new_resp.get()
				time.sleep(5)
				
			if retries == MAX_RETRIES:
				raise Exception('Max retries limit reached without success')
			
			location = status.conn.getresponse().getheader('location')
			return Resource(uri=urlparse(location).path, api=self._api, logger = self._logger, reraise_http_error = self._reraise_http_error, callback = self._callback).get()			
		
		return Response (self, resp)
		

class API(object):
	RESOURCE_CLASS = Resource
	
	REQ_TIMEOUT = 60
	def __init__(self, base_url, auth=None, logger = None, reraise_http_error = True, callback = None):
		self.base_url = base_url + '/' if not base_url.endswith('/') else base_url
		self.api_path = urlparse(base_url).path
		self.session = requests.Session ()
		self.auth = auth
		self.logger = logger
		self.reraise_http_error = reraise_http_error
		self.callback = callback

	def __getattr__(self, name):
		if name in ('get', 'post', 'put', 'patch', 'delete', 'options'):
			r = self.RESOURCE_CLASS (uri='', api=self, logger = self.logger, reraise_http_error = self.reraise_http_error, callback = self.callback)
			return getattr (r, name)
		return self.RESOURCE_CLASS (uri=name, api=self, logger = self.logger, reraise_http_error = self.reraise_http_error, callback = self.callback)
	
	def __call__(self, id):
		r = self.RESOURCE_CLASS (uri='', api=self, logger = self.logger, reraise_http_error = self.reraise_http_error, callback = self.callback)
		return r (id)
