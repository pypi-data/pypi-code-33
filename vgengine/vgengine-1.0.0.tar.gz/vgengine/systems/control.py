from cbd.component import ComponentABC as _ComponentABC
from cbd.system import SystemABC as _SystemABC

from collections import namedtuple as _struct
from enum import Enum as _Enum

class _ControlComponent(_ComponentABC):
	name = 'control'

class Inputs(_Enum):
	LEFT = 0
	RIGHT = 1
	UP = 2
	DOWN = 3
	A = 4

class Controller(_ControlComponent):
	name = 'controller'
	def __init__(self):
		super(Controller, self).__init__()
		self.keys = [0, 0, 0, 0]
		self.pressed = set()
		self.last_pressed = set()

	@property
	def actionsets(self):
		if self.parent:
			return self.parent.get_components(ActionSet)
		return []

	def press(self, *inputs):
		self.pressed = self.pressed.union(inputs)

	def apply_actions(self):
		for actionset in self.actionsets:
			actionset.apply_actions(self.pressed, self.last_pressed)
		self.last_pressed = self.pressed
		self.pressed = set()	

	@_ControlComponent.parent.setter
	def parent(self, new_parent):
		'''
		This is a lot simpler. 
		All we're doing is creating a singleton component.
		And then assigning that singleton as a property of the object.
		'''
		if new_parent:
			assert not new_parent.get_components(Controller), 'Only one controller per game object'
		_ControlComponent.parent.__set__(self, new_parent)
		if new_parent:
			setattr(new_parent, self.name, self)

class Keyboard(Controller):
	from pygame.locals import *

class Control(_SystemABC):
	name = 'control'
	component_type = _ControlComponent

	@property
	def controllers(self):
		return set(comp for comp in self.components if isinstance(comp, Controller))

	def key_press(self, pressed=frozenset(), **kwargs):
		for controller in self.controllers:
			if isinstance(controller, Keyboard):
				controller.press(*pressed)

	def update(self, **kwargs):
		super(Control, self).update(**kwargs)
		for controller in self.controllers:
			controller.apply_actions()

class PressType(_Enum):
	START = 0
	WHILE = 1
	END   = 2

Mapping = _struct('Mapping', 'inputs, action, press_type')

class ActionSet(_ControlComponent):
	name = 'actionset'
	mappings = []
	def __init__(self, mappings=[]):
		''' A set of mappings from inputs to actions '''
		super(ActionSet, self).__init__()
		self.mappings = mappings[:] if mappings else self.mappings

	def add_mapping(self, mapping):
		if mapping not in self.mappings:
			self.mappings.append(mapping)

	def remove_mapping(self, inputs):
		''' removes all mappings with the given set of inputs '''
		inputs = set(inputs)
		self.mappings[:] = [mapping for mapping in self.mapping 
								if mapping.inputs != inputs]

	def apply_actions(self, pressed, last_pressed=set()):
		try:
			pressed = set(pressed)
			last_pressed = set(last_pressed)
		except TypeError, e:
			print "'pressed' must be iterable"
			print e
		if not pressed:
			pressed = set()

		pressed_start = pressed.difference(last_pressed)
		pressed_end = last_pressed.difference(pressed)

		# How come python can't have real enums?
		for inputs, action, press_type in self.mappings:
			inputs = set(inputs)
			if press_type == PressType.START:
				if inputs.issubset(pressed_start):
					action(self.parent)

			# might have to do something more complicated if
			# we want behavior that doesn't rely on the entire
			# set of keys being pressed in exactly the same frame
			elif press_type == PressType.WHILE:	
				if inputs.issubset(pressed):
					action(self.parent)

			elif press_type == PressType.END:
				if inputs.issubset(pressed_end):
					action(self.parent)

	def __repr__(self):
		return "<%s Component - Keys: %r>" % (self.name, len(self.mappings))

if __name__ == '__main__':

	controller = Controller()
	def action_start(go): 
		print 'start'
	def action_while(go):
		print 'while'
	def action_end(go):
		print 'end'

	action_set = ActionSet([
		Mapping(set([1]), action_while, PressType.WHILE),
		Mapping(set([2]), action_start, PressType.START),
		Mapping(set([3]), action_end, PressType.END)])

	print '== (1, 2, _)'
	action_set.apply_actions((1, 2))
	print '== (1, 2, 3)'
	action_set.apply_actions((1, 2, 3), (1, 2))
	print '== (_, 2, 3)'
	action_set.apply_actions((2, 3), (1, 2, 3))
	print '== (_, _, 3)'
	action_set.apply_actions((3, ), (2, 3))
	print '== (_, _, _)'
	action_set.apply_actions(set(), (3, ))