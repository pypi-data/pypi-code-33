import pymunk as _pymunk
from pymunk import Vec2d

from weakref import WeakSet as _WeakSet

from cbd.system import SystemABC as _SystemABC
from cbd.component import ComponentABC as _ComponentABC
from cbd.event import Event

from collections import namedtuple as _namedtuple
from collections import defaultdict as _defaultdict

from collections import Iterable as _iter
from numbers import Number as _num
import math as _math

COLLISION = 'collision'
DISTANCE = 'distance'

class _PhysicsComponent(_ComponentABC):
	name = 'physics'


class Physics(_SystemABC):
	"""
	This is an abstract type. Should be used as such.
	I have no power over you, though.

	The main difference between this and pymunk alone 
	is the way collision detection is handled.
	"""
	name = 'physics'
	component_type = _PhysicsComponent

class Body(_PhysicsComponent):
	name = 'body'

	DYNAMIC = _pymunk.Body.DYNAMIC
	KINEMATIC = _pymunk.Body.KINEMATIC
	STATIC = _pymunk.Body.STATIC
	@_PhysicsComponent.parent.setter
	def parent(self, new_parent):
		"""Sets the parent object of this body.

		If current parent has shapes,
		the shapes will be removed from this body
		(assuming they were attached to the body)

		If the new_parent has shapes,
		the shapes of new_parent will 
		be attached to this body.
		"""
		if new_parent == self.parent:
			return

		if new_parent:
			assert not new_parent.get_components(Body), 'only one body per game object'
		if self.parent:
			for shape in self.parent.get_components(Shape):
				shape.parent = None
		if new_parent:
			for shape in new_parent.get_components(Shape):
				shape.body = self
		_PhysicsComponent.parent.__set__(self, new_parent)

class MaskAll(object):
	"""A bit mask that represents an infinite string of 1s"""
	def __and__(self, other):
		return other

	def __or__(self, other):
		return MaskAll()

	def __lshift__(self, other):
		return MaskAll()

	def __rshift__(self, other):
		return MaskAll()

	def __xor__(self, other):
		return ~other

	def __invert__(self):
		return 0

	def __repr__(self):
		return "*"

class Shape(_PhysicsComponent):
	"""
	The shape component defines the physical space an a body occupies.

	Shapes are attached to bodies via an offset. 
	Given a Circle shape attached to a body, an offset of (0, 0)
	places it directly in the center of the body.

	The offset does not have to be contained within the bounds of the shape.
	"""
	name = 'shape'
	def __init__(self, *args, **kwargs):
		super(Shape, self).__init__(*args, **kwargs)
		self._collision_layer = 0
		self._collision_mask = MaskAll()
		self._collision_group = 0
		self.collision_set = dict()
		self.separation_set = dict()

	def collision_update(self, *args, **kwargs):
		"""Updates the collision set of the shape"""
		for shape, collision_data in self.collision_set.iteritems():
			normal, solid, time = collision_data
			time += 1
			self.collision_set[shape] = CollisionData(normal, solid, time)
		self.separation_set = dict()

	def is_solid(self, shape, normal, types_equal=False):
		"""Determine if a collision is solid.

		If True, then objects will be allowed to collide physically.
		If False, then it blocks physical collisions.
		"""
		if types_equal:
			# only compare right most bit
			return bool((self.collision_mask & 1) & (shape.collision_mask & 1))
		# else, drop right most bit and compare
		return bool((self.collision_mask >> 1) & (shape.collision_mask >> 1))

	def in_layer(self, shape, normal):
		"""Determine if a collision happened in this layer.

		If True, objects are considered on the same layer and trigger overlap events.
		If False, then objects are not considered in the same layer.
		"""
		if self.collision_layer == None or shape.collision_layer == None:
			return False
		if not (self.collision_layer == shape.collision_layer):
			return False
		return True

	@property
	def collision_layer(self):
		"""Get the collision layer of this shape as an integer"""
		return self._collision_layer

	@collision_layer.setter
	def collision_layer(self, new_cl):
		"""Set the collision layer of this shape as an integer"""
		assert new_cl >= 0 or new_cl == None
		self._collision_layer = new_cl

	@property
	def collision_mask(self):
		"""Get the collision mask of the shape as an integer"""
		return self._collision_mask

	@collision_mask.setter
	def collision_mask(self, new_mask):
		"""Set the collision mask of the shape as an integer"""
		assert new_mask >= 0 or new_mask == None
		self._collision_mask = new_mask

	@_PhysicsComponent.parent.setter
	def parent(self, new_parent):
		"""Set the parent object of the shape. 

		If new_parent has a body, the shape will
		be attached to the new body and detached 
		from its current body."""
		if new_parent == self.parent:
			return
		if new_parent:
			bodies = new_parent.get_components(Body)
			assert(len(bodies) <= 1)
			if bodies:
				for body in bodies:
					self.body = body
			else:
				self.body = None
		_PhysicsComponent.parent.__set__(self, new_parent)
		
###############################################################################
###############################################################################

CollisionData = _namedtuple("CollisionData", "normal, solid, time")

# Continuous Physics style Physics
# This should be incredibly simple since we're inheriting from Pymunk.
# Essentially, we're just creating a wrapper to be able to handle.
class Physics2D(Physics):
	"""
	A system that models a continuous 2D physics environment
	as a set of Bodies with associated shapes.
	"""

	def __init__(self):
		super(Physics2D, self).__init__()
		self.space = _pymunk.Space()
		handler = self.space.add_default_collision_handler()
		handler.begin = self._default_collision_handler
		handler.separate = self._default_separation_handler

	def add(self, *physics_components):
		"""Add Bodies or Shapes to the physics system

		Bodies and shapes must be added for simulation to work"""
		super(Physics2D, self).add(*physics_components)
		self.space.add(*physics_components)

	def remove(self, *physics_components):
		"""Remove Bodies or Shapes from the physics system

		Bodies and shapes must be appropriately removed when no longer in use."""
		super(Physics2D, self).remove(*physics_components)
		self.space.remove(*physics_components)

	def update(self, fps, **kwargs):
		"""Steps the physics simulation forward by dt=1/fps"""
		dt = 1./fps
		self._events_internal = []
		for body in self.space.bodies:
			body.update(fps=fps, **kwargs)
		for shape in self.space.shapes:
			shape.collision_update(fps=fps, **kwargs)
		self.space.step(dt)

	def _default_collision_handler(self, arbiter, space, data):
		go1, go2 = [shape.parent for shape in arbiter.shapes]
		types_equal = go1.__class__ == go2.__class__

		sh1, sh2 = arbiter.shapes
		normal = arbiter.contact_point_set.normal
		if not (sh1.in_layer(sh2, -normal) and sh2.in_layer(sh1, normal)): 
			return False
		solid = sh1.is_solid(sh2, -normal, types_equal) and sh2.is_solid(sh1, normal, types_equal)
		sh1.collision_set[sh2] = CollisionData(normal, solid, 0)
		sh2.collision_set[sh1] = CollisionData(-1*normal, solid, 0)

		self.events.push(Event('collision', 
			game_objects=[go1, go2], data=data))

		return solid

	def _default_separation_handler(self, arbiter, space, data):
		go1, go2 = [shape.parent for shape in arbiter.shapes]
		types_equal = go1.__class__ == go2.__class__

		sh1, sh2 = arbiter.shapes
		normal = arbiter.contact_point_set.normal
		if sh2 not in sh1.collision_set:
			return False
		if not (sh1.in_layer(sh2, -normal) and sh2.in_layer(sh1, normal)):
			return False
		solid = sh1.is_solid(sh2, -normal, types_equal) and sh2.is_solid(sh1, normal, types_equal)
		del sh1.collision_set[sh2]
		del sh2.collision_set[sh1]

		sh1.separation_set[sh2] = CollisionData(normal, solid, None)
		sh2.separation_set[sh1] = CollisionData(-normal, solid, None)
		
		self.events.push(Event('separation', 
			game_objects=[go1, go2], data=data))

class Body2D(_pymunk.Body, Body):
	"""
	A Body models a point mass. 
	It has mass, momentum, drag, etc.
	Position, velocity.

	Forces can be applied to the body.

	You can also define a drag coefficient.

	Assigning gravity to a body overrides the gravity of the space.

	args:
		mass (float): mass of body
		body_type {Body.DYNAMIC, Body.KINEMATIC, Body.STATIC}
	"""
	def __init__(self, mass, body_type=Body.DYNAMIC):
		Body.__init__(self)
		assert mass > 0, "mass must be nonzero, positive number"
		super(Body2D, self).__init__(mass, float('inf'), body_type=body_type)
		self._gravity = None
		self.drag = 0
		self.last_position = self.position
		self.direction = None
			

	def update(self, **kwargs):
		"""Applies drag and gravity"""
		self.last_position = self.position
		if self.gravity != None:
			# Applied at world point, so angle of body isn't considered.
			self.apply_force_at_world_point((self.gravity-self.space.gravity)*self.mass, self.position)

		if self.drag != 0:
			drag_force = self.velocity*self.drag
			self.apply_force_at_world_point(-drag_force, self.position)

	@property
	def gravity(self):
		"""Get the gravity as a Vector"""
		return self._gravity

	@gravity.setter
	def gravity(self, new_gravity):
		"""Set the gravity of a dynamic body, overriding the gravity of the space."""
		self._gravity = Vec2d(new_gravity)

class StaticBody2D(Body2D):
	"""
	Models a body that doesn't move.
	Can be view as a body with infinite mass.
	Essentially, position remains constant, unless reassigned.
	"""
	def __init__(self):
		super(StaticBody2D, self).__init__(1, body_type=_pymunk.Body.STATIC)

class KinematicBody2D(Body2D):
	"""
	A Kinematic body can also be viewed as an object with infinite mass.
	The main difference is that it can also have a velocity.
	"""
	def __init__(self):
		super(KinematicBody2D, self).__init__(1, body_type=_pymunk.Body.KINEMATIC)

class PolyShape2D(_pymunk.Poly, Shape):
	"""
	Defines a polygon shape given a set of vertices (points in space).

	The Polygon is generated from the vertices in a counter-clockwise fashion.

	So a square could be defined with 
	vertices =  [(0, 0), (10, 0), (10, 10), (0, 10)]

	Starting from left to write, moving counter clockwise, it is drawn
	bottomleft, bottomright, topright, topleft

	args:
		vertices (list of points)
		offset (point)
	"""
	def __init__(self, vertices, offset=(0, 0)):
		vertices = [(v[0]+offset[0], v[1]+offset[1]) for v in vertices]
		self.offset = offset
		super(PolyShape2D, self).__init__(None, vertices)
		Shape.__init__(self)

class LineSegment(_pymunk.Segment, Shape):
	"""
	Defines a line segment
	Connecting two points in space, and has a radius (width)

	args:
		a (point): start point
		b (point): end point
		radius (float)
		offset (point)
	"""
	def __init__(self, a, b, radius, offset=(0, 0)):
		self.offset = offset
		super(LineSegment, self).__init__(None, a, b, radius)
		Shape.__init__(self)

class CircleShape2D(_pymunk.Circle, Shape):
	"""
	Defines a circle with a given radius

	args:
		radius (float)
	"""
	def __init__(self, radius, offset=(0, 0)):
		super(CircleShape2D, self).__init__(None, radius, offset)
		Shape.__init__(self)

class RectShape2D(PolyShape2D):
	"""
	Defines a rectangle with width and height.

	The offset applies to the center of the rectangle,
	which is defined by half the width and height

	args:
		width (int)
		height (int)
		offset (point)
	"""
	def __init__(self, width, height, offset=(0, 0)):
		right, left = width/2., -width/2.
		top, bottom = height/2., -height/2.
		vertices = [(left, top), (left, bottom), (right, bottom), (right, top)]
		super(RectShape2D, self).__init__(vertices, offset)

class BoxShape2D(RectShape2D):
	"""
	Legacy. Identical to RectShape2D.

	args:
		size  ((width, height))
		offset (point)
	"""
	def __init__(self, (width, height), offset=(0, 0)):
		super(BoxShape2D, self).__init__(width, height, offset)

class SquareShape2D(RectShape2D):
	"""
	Defines a perfect square

	args:
		size (int)
		offset (point)
	"""
	def __init__(self, size, offset=(0, 0)):
		super(SquareShape2D, self).__init__(size, size, offset)

class LayeredRect2D(RectShape2D):
	"""
	A rectangle that uses its collision normal to determine collision layers.

	If it normal of a collision is equual to its solid_normal,
	then the collision will be solid. Otherwise, no collision is triggered.

	args:
		width (int)
		height (int)
		normal (unit vector)
		offset (point)
	"""
	def __init__(self, width, height, normal=(0, -1), offset=(0, 0)):
		super(LayeredRect2D, self).__init__(width, height, offset)
		self._solid_normal = Vec2d(normal)

	@property
	def solid_normal(self):
		"""get the collision normal for which the object is solid"""
		return self._solid_normal

	@solid_normal.setter
	def solid_normal(self, new_solid_normal):
		"""Set the collision normal for which the object is solid"""
		self._solid_normal = Vec2d(new_solid_normal)

	def in_layer(self, shape, normal):
		"""Determine if the object is in the same layer based on solid_normal"""
		in_layer = super(LayeredRect2D, self).in_layer(shape, normal)
		error = abs((normal.angle-self.solid_normal.angle)/self.solid_normal.angle)
		return in_layer and error <= 0.15

class DirectionalRect2D(LayeredRect2D):
	"""
	Same as layered rect.
	"""
	def in_layer(self, shape, normal):
		return Shape.in_layer(self, shape, normal)

	def is_solid(self, shape, normal, types_equal=False):
		return (LayeredRect2D.in_layer(self, shape, normal) and 
			    super(LayeredRect2D, self).is_solid(shape, normal, types_equal))

class Space2DGrid(object):
	def __init__(self):
		self._bodies = set()

	@property
	def bodies(self):
		return frozenset(self._bodies)

	def _add(self, body):
		assert isinstance(body, Body2DGrid), "Can only add BodyGrid types to space"
		self._bodies.add(body)

	def add(self, *bodies):
		for body in bodies:
			self._add(body)

	def _remove(self, body):
		if body in self.bodies:
			self._bodies.remove(body)

	def remove(self, *bodies):
		for body in bodies:
			self._remove(body)

	def _step(self, body, dt, revert=False):
		if body.body_type == Body.STATIC:
			return
		x, y = body.position
		vx, vy = body.velocity
		if revert:
			body.position = x-vx, y-vy
			body.velocity = (0, 0)
		else:
			body.position = x+vx, y+vy

	def step(self, dt=1):
		"""How does dt effect the motion of objects?"""
		positions = _defaultdict(lambda : set())
		for body in self._bodies:
			self._step(body, dt)
			positions[body.position].add(body)
			# this shouldn't happen every step?

		# check_collisions = True
		# while check_collisions:
		# 	check_collisions = False
		# 	for position, bodies in positions.iteritems():
		# 		dynamic
		# 		if len(bodies) > 1 and any([b.body_type == Body.DYNAMIC])
				
		# 		while len(bodies) > 1 and dynamic_bodies:
		# 			for body in dynamic_bodies:
					
				# have to resolve collisions

		# maybe kill some things here?


	def __repr__(self):
		return "<Space 2DGrid>"


class Physics2DGrid(Physics):
	"""
	Grid with no edges
	"""
	def __init__(self):
		super(Physics2DGrid, self).__init__()
		self.space = Space2DGrid()

	def add(self, *components):
		super(Physics2DGrid, self).add(*components)
		for component in components:
			self.space.add(component)

	def remove(self, *components):
		super(Physics2DGrid, self).remove(*components)

	def update(self, fps, **kwargs):
		dt = 1./fps
		for body in self.space.bodies:
			body.update()
		self.space.step(dt)
			

class Body2DGrid(Body):
	def __init__(self, body_type=Body.DYNAMIC):
		super(Body2DGrid, self).__init__()
		self.body_type = body_type
		self._angle = 0
		self._position = (0, 0)
		self._velocity = (0, 0)
		self._space = None

	@property
	def angle(self):
		return self._angle

	@property
	def space(self):
		return self._space

	@property
	def position(self):
		return self._position

	@position.setter
	def position(self, new_pos):
		assert isinstance(new_pos, tuple)
		assert len(new_pos) == 2
		assert isinstance(new_pos[0], _num)
		assert isinstance(new_pos[1], _num)
		x, y = new_pos

		self._position = int(x), int(y)

	@property
	def velocity(self):
		return self._velocity

	@velocity.setter
	def velocity(self, new_vel):
		assert isinstance(new_vel, tuple) and len(new_vel) == 2, "Velocity has to be tuple of type (int, int)"
		x, y = new_vel
		assert (x in [-1, 0, 1] and y == 0) or (y in [-1, 0, 1] and x == 0), "Velocity can't have magnitude greater than 1"
		self._velocity = (x, y)

	def __repr__(self):
		return "<GridBody: pos%r | vel%r>" % (self.position, self.velocity)

if __name__ == '__main__':

	physics = Physics2D()
	body = Body2D(10)
	static_body = StaticBody2D()
	kinematic_body = KinematicBody2D()
	shape = BoxShape2D((10, 10))

	grid_physics = Physics2DGrid()
	grid_body = Body2DGrid()
	grid_physics.add(grid_body)
	
	grid_body.velocity = (1, 0)
	print grid_physics.space, grid_physics.space.bodies
	grid_physics.update()
	print grid_physics.space.bodies




	


