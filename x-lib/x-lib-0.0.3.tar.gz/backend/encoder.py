import calendar
from datetime import datetime
from decimal import Decimal
from flask.json import JSONEncoder
import time


class JsonEncoder(JSONEncoder):
	
	def default(self, obj):
		try:
			if isinstance(obj, (bytes, bytearray)):
				return obj.decode("ASCII")
			elif isinstance(obj, Decimal):
				return float(obj)
			elif isinstance(obj, datetime):
				millis = int(time.mktime(obj.timetuple()) * 1000)
				return millis
		except TypeError:
			raise
		return JSONEncoder.default(self, obj)
