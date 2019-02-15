class EventQueue(object):
	"""
	A simple container for events.

	Can only store events.
	"""
	def __init__(self):
		self._events = []

	def pop(self):
		"""Gets the next event in the queue"""
		return self._events.pop(0)

	def get(self):
		"""Gets all the events in the queue, subsequently clearing the queue"""
		events = self._events[:]
		self._events = []
		return events

	def push(self, *events):
		"""Push events onto the queue"""
		for event in events:
			assert isinstance(event, Event), "event queue can only push events"
			self._events.append(event)

class Event(object):
	"""
	An Event has a type and can store information about such an event.

	The **kwargs are converted into accessible properties/items.

	>> click_event = Event('click', position=(10, 15))
	>> print click_event.position
	(10, 15)
	>> print click_event['position']
	(10, 50)

	"""
	_type = 'default_event'
	def __init__(self, event_type, **kwargs):
		self._type = event_type
		self._attrs = kwargs

	def __getattr__(self, attr):
		if attr in self._attrs:
			return self._attrs[attr]
		raise AttributeError("event doesn't have attribute %r" % attr)

	def __getitem__(self, atrr):
		return self._attrs[attr]

	@property
	def type(self):
		"""Returns the event type as a string"""
		return self._type

	def __str__(self):
		return "<Event('%s')>" % self.type
