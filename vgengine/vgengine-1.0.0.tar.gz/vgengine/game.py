from cbd.event import *

from systems import graphics, physics, control

from collections import defaultdict

"""
I need a better abstraction for Game and Scene.

I thought a game would be the system manager, 
but the scene contains all the objects that need to be updated.

So, is a scene just a container of game object instances
that get loaded into the game and ar run that way?
"""
class Game(object):
	""" 
	A game is a scene manager.

	When creating your own environment,
	you should create a new container for scenes.

	For instance, maybe you want an environment
	to test AI, then you should create a class
	(possibly a base class) of Game with custom
	functions when initializing, updating, and quitting a scene.

	If you want to change the graphics, 
	use a different Graphics system.
	Then, pass in the the display created by that Graphics
	Graphics.create_display(**kwargs) function into Game.run(display)

	"""
	def __init__(self, *scenes):
		"""
		Create a container for scenes. 
		The scenes will e played in order 
		of addition
		"""
		self._running = False
		self.scenes = []
		self._scene = None
		self.add(*scenes)

	running = property(lambda : self._running)

	def add(self, *scenes):
		for scene in scenes:
			self._add_scene(scene)

	def remove(self, *scenes):
		for scene in scenes:
			self._remove_scene(scene)

	def _add_scene(self, scene):
		"""
		Kind of like the camera, probably need a way
		of being able to define the order of the scenes.
		(keep it in a list?)
		"""
		if scene._game:
			scene._game.remove(scene)
		scene._game = self
		self.scenes.append(scene)
		if self._scene == None:
			self._scene = scene

	def _remove_scene(self, scene):
		scene._game = None
		self.scenes.remove(scene)
		if self._scene == scene and self.scenes:
			self._scene = self.scenes[0]

	@property
	def scene(self):
		return self._scene

	@scene.setter
	def scene(self, new_scene):
		if self.running:
			if self.scene:
				self.scene.quit()
			new_scene.init()
		self._scene = new_scene

	def quit(self):
		self._running = False

	def on_quit(self):
		"""
		Callback functions for when a scene quits.
		"""
		pass

	def init(self):
		pass

	def on_init(self):
		"""
		Callback function for when a scene initializes
		"""
		pass

	def update(self):
		pass

	def on_update(self):
		"""
		Callback function for when a 
		"""
		pass

	def run(self, **kwargs):
		"""
		Plays through the scenes of the game, or something.
		"""
		# do some scene logic
		self.scene.init(**kwargs)
		self.on_init()
		self._running = True
		while self._running:
			self.scene.receive(**kwargs)
			self.scene.update(**kwargs)
			self.scene.display(**kwargs)
			self.on_update()
		self._running = False
		self.scene.quit(**kwargs)
		self.on_quit()


class Scene(object):
	"""
	A scene is a system and room manager

	Physics should define the space of the world and handle physics
	bodies, forces, collisons, etc..

	Graphics should be a way for you to look into the space 
	and handle images or other things used for display.
	"""
	def __init__(self, *systems):
		self._systems = set()
		self._game = None
		for system in systems:
			self._add_system(system)

		self._systems_sorted = sorted(self._systems, key=self._sort_key)
		self._game_objects = set()

		self._event_handlers = defaultdict(lambda: [])

		self.events = EventQueue()


	@property
	def room(self):
		raise AttributeError("'rooms' has been depricated - just use scene.game_objects")
		
	def _sort_key(self, sys):
		if isinstance(sys, graphics.Graphics): return 3
		elif isinstance(sys, physics.Physics): return 2
		elif isinstance(sys, control.Control): return 0
		return 1

	def _add_system(self, system):
		assert not hasattr(self, system.name), "scene already has this system"
		setattr(self, system.name, system)
		self._systems.add(system)

	@property
	def game(self):
		return self._game

	@property
	def game_objects(self):
		return list(self._game_objects)

	@property
	def components(self):
		return list(c for sys in self._systems for c in sys.components)

	@property
	def systems(self):
		return list(self._systems)

	def add(self, *game_objects):
		"""
		add game_object to the scene
		"""
		for game_object in game_objects:
			self._add_game_object(game_object)

	def remove(self, *game_objects):
		"""
		remove game_objects from the scene
		"""
		for game_object in game_objects:
			self._remove_game_object(game_object)

	def _add_game_object(self, game_object):
		"""
		private add a single game_object to the scene
		"""
		if game_object._scene:
			game_object._scene._remove_game_object(game_object)
		game_object._scene = self
		self._add_components(*game_object.components)
		self._game_objects.add(game_object)

	def _add_components(self, *components):
		for component in components:
			for system in self.systems:
				if isinstance(component, system.component_type):
					system.add(component)

	def _remove_components(self, *components):
		for component in components:
			if component.system:
				component.system.remove(component)

	def _remove_game_object(self, game_object):
		"""
		private remove a single game_object from the scene
		"""
		if not game_object._scene:
			return
		self._remove_components(*game_object.components)
		self._game_objects.remove(game_object)
		game_object._scene = None

	def add_event_handler(self, event_type, callback):
		self._event_handlers[event_type].append(callback)

	def _handle_events(self):
		for system in self.systems:
			for event in system.events.get():
				for callback in self._event_handlers[event.type]:
					callback(self, event)
		# Handling events has the potential to trigger more events
		for event in self.events.get():
			for callback in self._event_handlers[event.type]:
				callback(self, event)

	def _update_systems(self, **kwargs):
		for system in self.systems:
			system.update(**kwargs)
			
	def update(self, **kwargs):
		# updates the systems of the scene
		self._handle_events()
		self._update_systems(**kwargs)

	def display(self, **kwargs):
		if hasattr(self, 'graphics'):
			self.graphics.display(**kwargs)

	def receive(self, **kwargs):
		if hasattr(self, 'control'):
			if hasattr(self, 'graphics'):
				self.control.key_press(pressed=self.graphics.get_inputs(**kwargs), **kwargs)

	def init(self, **kwargs):
		for system in self.systems:
			system.init(**kwargs)

	def quit(self, **kwargs):
		self.remove(*self.game_objects)
		for system in self.systems:
			system.quit(**kwargs)


class GameObject(object):
	"""
	Attach components to the game object 
	to give it its functionality and bring it to life in the game.

	Game objects can only have one physics body.
	"""
	def __init__(self, *components):
		self._scene = None
		self._components_sorted = []
		self._components = set()
		self.add(*components)
		
	scene = property(lambda self: self._scene)

	def add(self, *components):
		for component in components:
			self._add_component(component)
		if self.scene:
			self.scene._add_components(*components)

	def remove(self, *components):
		for component in components:
			self._remove_component(component)
		if self.scene:
			self.scene._remove_components(*components)

	def _add_component(self, component):
		"""
		Currently restricting to one body component per game object
		This is implicit. Adding another body to the game object
		will replace the old game object, and reattach the shapes
		and sprites from thet body to the new one. 

		The same goes for Controllers and ActionSets
		"""

		# This is so subtle, I don't even know what to say.
		# But, assigning a new parent triggers a decorater
		# which may or may not do a lot of complicated stuff
		# related to combining certain components together.
		# (Go look at the Physics body/shape parent decorator)
		if component not in self._components:
			component.parent = self
			self._components.add(component)
			self._components_sorted = sorted(self._components, key=self._sort_key)

	def _remove_component(self, component):
		component.parent = None
		self._components.remove(component)
		self._components_sorted.remove(component)

		
		
	def _sort_key(self, comp):
		if isinstance(comp, graphics._GraphicsComponent): return 3
		elif isinstance(comp, physics._PhysicsComponent): return 2
		elif isinstance(comp, control._ControlComponent): return 0
		return 1


	@property
	def components(self):
		"""Returns components sorted by order of update"""
		return list(self._components_sorted)

	def get_components(self, component_type=None):
		"""
		returns a list of components of the given type.
		"""
		return [component for component in self._components 
									if (component_type and isinstance(component, component_type)) 
									or component_type == None]
