import time

class UnwiredRequest:
	"""
	A request object for the Unwiredlabs location API.
	This class does all encoding that is needed.
	"""

	#
	# Public API
	#

	def __init__(self, device_id=None, key=None, mcc=None, mnc=None, fetch_address=False):
		"""
		Initialize an empty request

		:param device_id: device ID for this request if on a per device plan
		:param key: API key, may be skipped if set in ``UnwiredConnection``
		:param mcc: Mobile country code of the GSM Network, optional, shortcut if you want to skip it on adding Celltowers
		:param mnc: Mobile network code of the GSM Network, optional, shortcut if you want to skip it on adding Celltowers
		:param fetch_address: Set to ``true`` to fetch an address string with the response
		"""

		self.device_id = device_id
		self.aps = []
		self.gsmTowers = []
		self.lteTowers = []
		self.cdmaTowers = []
		self.umtsTowers = []
		self.gpsCoordinate = None
		self.mcc = mcc
		self.mnc = mnc
		self.key = key
		self.fetch_address = fetch_address

	def __str__(self):
		return '<UnwiredRequest: {wifi} WIFI APs, {tower} cell towers{gps}>'.format(
			wifi=len(self.aps),
			tower=len(self.gsmTowers) + len(self.lteTowers) + len(self.cdmaTowers) + len(self.umtsTowers),
			gps=', GPS: {lat}, {lon}'.format(lat=self.gpsCoordinate['lat'], lon=self.gpsCoordinate['lon']) if self.gpsCoordinate else ''
		)

	def addAccessPoint(self, BSSID, rssi, band='unknown'):
		"""
		Add WIFI station to search request

		:param BSSID: WIFI BSSID, hex encoded
		:param rssi: signal strength in dBm
		:param band: WIFI band, one of 'unknown', '2.4', 5.0'
		"""

		self.aps.append({
			'bssid': BSSID,
			'rssi': rssi,
			'band': band
		})

	def addGSMCellTower(self, lac, cellID, rssi, mcc=None, mnc=None):
		"""
		Add GSM Cell tower to search request

		:param lac: location area code
		:param cellID: celltower ID
		:param rssi: signal strength in dBm
		:param mcc: mobile country code, may be skipped if set on request initialization
		:param mnc: mobile network code, may be skipped if set on request initialization
		"""

		if self.mcc is None and mcc is None:
			raise RuntimeError('Either set mcc on initialization or provide it when adding a cell tower')
		if self.mnc is None and mnc is None:
			raise RuntimeError('Either set mcc on initialization or provide it when adding a cell tower')
		if mcc is None:
			mcc = self.mcc
		if mnc is None:
			mnc = self.mnc

		self.gsmTowers.append({
			'mcc': mcc,
			'mnc': mnc,
			'lac': lac,
			'cellID': cellID,
			'rssi': rssi
		})

	def addLTECellTower(self, lac, cellID, rssi, mcc=None, mnc=None):
		"""
		Add LTE Cell tower to search request

		:param lac: location area code
		:param cellID: celltower ID
		:param rssi: signal strength in dBm
		:param mcc: mobile country code, may be skipped if set on request initialization
		:param mnc: mobile network code, may be skipped if set on request initialization
		"""

		if self.mcc is None and mcc is None:
			raise RuntimeError('Either set mcc on initialization or provide it when adding a cell tower')
		if self.mnc is None and mnc is None:
			raise RuntimeError('Either set mcc on initialization or provide it when adding a cell tower')
		if mcc is None:
			mcc = self.mcc
		if mnc is None:
			mnc = self.mnc

		self.lteTowers.append({
			'mcc': mcc,
			'mnc': mnc,
			'lac': lac,
			'cellID': cellID,
			'rssi': rssi
		})

	def addCDMACellTower(self, lac, cellID, rssi, mcc=None, mnc=None):
		"""
		Add CDMA Cell tower to search request

		:param lac: location area code
		:param cellID: celltower ID
		:param rssi: signal strength in dBm
		:param mcc: mobile country code, may be skipped if set on request initialization
		:param mnc: mobile network code, may be skipped if set on request initialization
		"""

		if self.mcc is None and mcc is None:
			raise RuntimeError('Either set mcc on initialization or provide it when adding a cell tower')
		if self.mnc is None and mnc is None:
			raise RuntimeError('Either set mcc on initialization or provide it when adding a cell tower')
		if mcc is None:
			mcc = self.mcc
		if mnc is None:
			mnc = self.mnc

		self.cdmaTowers.append({
			'mcc': mcc,
			'mnc': mnc,
			'lac': lac,
			'cellID': cellID,
			'rssi': rssi
		})

	def addUMTSCellTower(self, lac, cellID, rssi, mcc=None, mnc=None):
		"""
		Add UMTS Cell tower to search request

		:param lac: location area code
		:param cellID: celltower ID
		:param rssi: signal strength in dBm
		:param mcc: mobile country code, may be skipped if set on request initialization
		:param mnc: mobile network code, may be skipped if set on request initialization
		"""

		if self.mcc is None and mcc is None:
			raise RuntimeError('Either set mcc on initialization or provide it when adding a cell tower')
		if self.mnc is None and mnc is None:
			raise RuntimeError('Either set mcc on initialization or provide it when adding a cell tower')
		if mcc is None:
			mcc = self.mcc
		if mnc is None:
			mnc = self.mnc

		self.umtsTowers.append({
			'mcc': mcc,
			'mnc': mnc,
			'lac': lac,
			'cellID': cellID,
			'rssi': rssi
		})

	def setGPSCoordinate(self, lat, lon, numSatelites, altitude=None, speed=None, hpe=0):
		"""
		Add a GPS coordinate to help Skyhook make their DB better

		:param lat: latitude, positive for South
		:param lon: longitude, positive for East
		:param numSatelites: number of visible satelites
		:param altitude: altitude above null, optional
		:param speed: speed, optional
		:param hpe: precision in meters, optional
		"""

		self.gpsCoordinate = {
			'latitude': lat,
			'longitude': lon,
			'accuracy': hpe if hpe != 0 else 50
		}

		if speed is not None:
			self.gpsCoordinate['speed'] = speed
		if altitude is not None:
			self.gpsCoordinate['altitude'] = altitude


	def serialize(self, key=None):
		"""
		Serialize a request into it's json form

		:param key: API key, optional if set on initialization
		"""

		result = {}

		if key:
			self.key = key

		if not self.key:
			raise RuntimeError('No API key set')

		result['token'] = self.key
		if self.device_id:
			result['id'] = self.device_id

		# radio type
		if len(self.gsmTowers)  > 0 and len(self.umtsTowers) == 0 and len(self.lteTowers) == 0 and len(self.cdmaTowers) == 0:
			result['radio'] = 'gsm'
		if len(self.gsmTowers) == 0 and len(self.umtsTowers)  > 0 and len(self.lteTowers) == 0 and len(self.cdmaTowers) == 0:
			result['radio'] = 'umts'
		if len(self.gsmTowers) == 0 and len(self.umtsTowers) == 0 and len(self.lteTowers)  > 0 and len(self.cdmaTowers) == 0:
			result['radio'] = 'lte'
		if len(self.gsmTowers) == 0 and len(self.umtsTowers) == 0 and len(self.lteTowers) == 0 and len(self.cdmaTowers)  > 0:
			result['radio'] = 'cdma'

		result['cells'] = self.serializeCellTower()
		result['address'] = 1 if self.fetch_address else 0
		result['wifi'] = self.serializeAP()
		result['fallbacks'] = ['lacf', 'scf']
		# result['ip'] = self.ip
		result['bt'] = 0  # only land coordinates

		return result

	def serialize_contrib(self):
		"""
		Serialize a request into it's json form for the contribute API

		:param key: API key, optional if set on initialization
		"""

		if not self.gpsCoordinate:
			return None

		result = {}

		result['timestamp'] = int(time.time())
		result['position'] = self.gpsCoordinate
		result['cells'] = self.serializeCellTower()
		result['wifi'] = self.serializeAP()

		return {"items": [ result ] }

	#
	# Internal
	#

	def serializeAP(self):
		"""
		Serialize WIFI APs for payload

		:return: Serialized WIFI APs as array
		"""

		result = []
		for ap in self.aps:
			item = {
				"bssid": ap['bssid'],
				"signal": ap['rssi']
			}
			result.append(item)

		return result


	def serializeCellTower(self):
		"""
		Serialize cell tower data for payload

		:return: Serialized cell tower payload as array
		"""

		result = []
		towers_list = [
			('gsm', self.gsmTowers),
			('lte', self.lteTowers),
			('cdma', self.cdmaTowers),
			('umts', self.umtsTowers)
		]
		for radio, towers in towers_list:
			for tower in towers:
				item = {
					"radio": radio,
					"mcc": tower['mcc'],
					"mnc": tower['mnc'],
					"lac": tower['lac'],
					"cid": tower['cellID'],

				}
				if tower['rssi'] <= -51 and tower['rssi'] >= -113:
					item['signal'] = tower['rssi']
				result.append(item)
		return result
