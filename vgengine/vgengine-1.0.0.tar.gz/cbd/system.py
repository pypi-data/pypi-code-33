from event import EventQueue
from component import ComponentABC
"""
This code is purely a guidline for implementing systems.

Using it as an interface became too much of a hassle. 
"""

class SystemABC(object):
	"""base class for containers of components

	AbstractSystem is used to instantiate a component
	so that it can be attached to other components. 

	This allows the component to have its own logic
	separate from its attachment and its own system
	that will update the components within that system.

	A system will have constructors for its own well
	defined compnonents and so an instance of the base
	class should never actually be created

	How a system stores and handles its components is
	entirely up to it, but it can use the default 
	_add_default function if it wants to use 
	the internal update
	"""
	
	name = 'system'
	component_type = ComponentABC
	def __init__(self):
		"""
		Overriding __init__ allows you to override the 
		default way to store components.
		As long as you override the other helper
		functions, it will work fine.
		"""
		self._new_components = set()
		self._components = set()
		self.events = EventQueue()

	def remove(self, *components):
		"""Remove components from the system"""
		for component in components:
			self._remove_component(component)

	def _remove_component(self, component):
		assert isinstance(component, self.component_type)
		component._system = None
		if component in self._components: 
			self._components.remove(component)
		if component in self._new_components:
			self._new_components.remove(component)

	def __contains__(self, component):
		"""Check if a component is in the system"""
		if component in self.components:
			return True
		return False

	def add(self, *components):
		"""Add components to the system"""
		for component in components:
			self._add_component(component)

	def _add_component(self, component):
		assert isinstance(component, self.component_type)
		component._system = self
		self._new_components.add(component)

	@property
	def components(self):
		"""Get a copy of the list of components"""
		return list(self._components.union(self._new_components))

	def initialize_new_components(self, **kwargs):
		"""Call on new components after System has already been initialized"""
		for component in list(self._new_components):
			component.init(**kwargs)
			self._components.add(component)
			self._new_components.remove(component)

	def init(self, **kwargs):
		"""Initialize the system and its components"""
		self.initialize_new_components(**kwargs)

	def update(self, **kwargs):
		"""Update the system and its components"""
		self.initialize_new_components(**kwargs)
		for component in self.components:
			component.update(**kwargs)
	
	def quit(self, **kwargs):
		"""Quit the system. Calls quit on all components and removes them from the system"""
		for component in self.components:
			component.quit(**kwargs)
			self.remove(component)
		self._components = set()

	def __str__(self):
		return "<%s System>" % self.name

	def __repr__(self):
		return self.__str__()