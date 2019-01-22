import datetime


class InvalidDataError(RuntimeError):
	"""
	Error class raised when the payload received from the Unwiredlabs server is somehow corrupt
	"""

	pass

class UnwiredResponse:
	"""
	Response deserializer class
	"""

	#
	# Public API
	#

	def __init__(self, data):
		"""
		Initialize the response class with data

		:param data: the data from the Unwiredlabs response
		"""

		if not data:
			raise RuntimeError('No response data set')

		self.data = data.json()
		self.status = 'Undefined'
		self.lat = None
		self.lon = None
		self.hpe = None
		self.date = None
		self.balance = None
		self.address = None
		self.deserialize()

	@property
	def coordinate(self):
		"""
		Fetch coordinate

		:return: Coordinate tuple (lat,long) if payload was not an error, else ``None``
		"""
		if self.status == 'Ok':
			return (self.lat, self.lon)
		else:
			return None

	#
	# Internal
	#

	def deserialize(self):
		"""
		Deserialize a response
		"""

		self.status = self.data['status'].title()
		if self.status == 'Ok':
			self.lat = self.data['lat']
			self.lon = self.data['lon']
			self.hpe = self.data['accuracy']
			self.balance = self.data['balance']
			self.address = self.data.get('address', None)
		else:
			self.status = self.data['message']
