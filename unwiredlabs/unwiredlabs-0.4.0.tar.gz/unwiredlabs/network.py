import requests
from .response import UnwiredResponse


class UnwiredConnection:
	"""
	Unwiredlabs server connection class.

	You may specify a custom server by supplying ``server``, defaults to the EU server.
	If you only use one account on that connection you may specify your API Key ``key``
	while initializing this
	"""

	def __init__(self, server='eu1.unwiredlabs.com', key=None, contribute_key=None, contribute_sandbox=True, timeout=10):
		self.session = requests.Session()
		self.server = server
		self.key = key
		self.timeout = timeout
		self.contribute_key = contribute_key
		self.contribute_sandbox = contribute_sandbox

	def performRequest(self, request):
		"""
		Perform a request on the connection and return the response, blocks until response received
		This may throw network and runtime errors when something goes wrong.

		:param request: the request to perform
		:return: ``UnwiredResponse`` object with the response
		"""
		headers = {
			"ContentType": "application/json",
			"Accept": "application/json"
		}
		request = requests.Request(
			"POST",
			"https://{}/v2/process.php".format(self.server),
			headers=headers,
			json=request.serialize(key=self.key)
		)
		prep = self.session.prepare_request(request)
		response = self.session.send(prep, timeout=self.timeout)
		return UnwiredResponse(response)

	def performContributeRequest(self, request):
		"""
		Perform a contribution API request, only works for requests that contain a GPS coordinate
		and a device ID. Setup ``contribute_key`` before calling.
		Will return 400 on requests that do not match the requirements.

		:param request: the request to perform
		:return: HTTP Status code of the response
		"""
		if not request.gpsCoordinate or not request.device_id or not self.contribute_key:
			return 400 # Do not send back data without GPS

		headers = {
			"ContentType": "application/json",
			"Accept": "application/json"
		}
		request = requests.Request(
			"POST",
			"https://d1.unwiredlabs.com/geosubmit.php?sbox={sandbox}&key={key}&id={device}".format(
				sandbox=1 if self.contribute_sandbox else 0,
				key=self.contribute_key,
				device=request.device_id
			),
			headers=headers,
			json=request.serialize_contrib()
		)
		prep = self.session.prepare_request(request)
		response = self.session.send(prep)
		return response.status_code
