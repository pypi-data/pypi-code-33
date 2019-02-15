class ComponentABC(object):
	"""
	A component is owned by a system,
	initialized by a system,
	updated by a system,
	quit from a system.

	A component can have a parent object, 
	and can use functionality and proprties
	together with other components owned by the object. 
	"""

	name = None
	def __init__(self):
		self._parent = None
		self._system = None

	def init(self, **kwargs):
		pass

	def update(self, **kwargs):
		pass

	def quit(self, **kwargs):
		pass

	@property
	def parent(self):
		"""Get the parent object"""
		return self._parent

	@parent.setter
	def parent(self, new_parent):
		"""Set the parent object"""
		if hasattr(self._parent, self.name) and new_parent != self._parent:
			delattr(self._parent, self.name)
		if new_parent != None:
			setattr(new_parent, self.name, self)
		self._parent = new_parent


	@property
	def system(self):
		"""Get the owning system"""
		return self._system

	@system.setter
	def system(self, new_system):
		"""Set the owning system"""
		if self._system:
			self._system.remove(self)
		if new_system:
			new_system.add(self)
		self._system = new_system

	def __str__(self):
		return '<%s Component>' % self.name

	def __repr__(self):
		return self.__str__()