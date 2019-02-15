import pygame as _pygame
import math as _math

from cbd.system import SystemABC as _SystemABC
from cbd.component import ComponentABC as _ComponentABC
from cbd.event import Event, EventQueue

class _GraphicsComponent(_ComponentABC):
	name = 'graphics'

class Graphics(_SystemABC):
	"""
	An abstract base class for the Graphics system
	"""
	name = 'graphics'
	component_type = _GraphicsComponent
	def display(self, **kwargs):
		raise NotImplementedError("subclass should implement this")


class Sprite(_GraphicsComponent):
	name = 'sprite'


"""
I'm trying really hard to create some kind of restriction
on the types of objects that can interact with eachother
These are 2D graphics to be associated with the 2D physics.

The coordinate system are defined as such:

	    |+y
	    |
	    |   
_-x___(0,0)___+x_
	    |
	    |
	    |-y

Everything is set up so that the camera is initialized at (0, 0),
and subsequently, the center of the display is (0, 0).

It doesn't make since to have a camera if you don't have a world to put 
it in... Depending on that world, it doesn't make sense to have a camera.
A 2D world needs a Camera. A 3D world needs a camera. Should these graphics
subclass some kind of GraphicsPhysical? I need to stop overthinking this.

I also realize now that the Graphics system itself is going to have to handle
SDL input/output in general.
"""
class Graphics2D(Graphics):
	from pygame.locals import *
	event_map = {
		QUIT : ('quit', ()),
		VIDEORESIZE : ('resize', ('size', 'w', 'h')), 
		MOUSEBUTTONDOWN : ('click', ('pos', 'button')),
		MOUSEBUTTONUP: ('unclick', ('pos', 'button')),
		KEYDOWN: ('keydown', ('unicode', 'key', 'mod')),
		KEYUP: ('keyup', ('key', 'mod'))}
	
	def quit(self, display=None, **kwargs):
		if display:
			self.destroy_display(display)

	@classmethod
	def create_display(self, resolution=(0, 0), flags=0, depth=0):
		return _pygame.display.set_mode(resolution, flags, depth)

	@classmethod
	def destroy_display(self, display):
		if display:
			_pygame.display.quit()

	@classmethod
	def get_inputs(self, display, **kwargs):
		if display:
			return frozenset(i for i, inp in enumerate(_pygame.key.get_pressed()) if inp)
		return frozenset()

	@classmethod
	def convert(self, position, display, camera):
		if display == None: 
			return (0, 0)

		display_surface = display.get_surface()
		if display_surface == None: 
			return (0, 0)

		display_rect = display_surface.get_rect()
		x, y = position
		camera_x, camera_y = camera.position
		fit_rect = camera.view.fit(display_rect)
		fit_rect.center = display_rect.center
		# position is center of camera
		camera_x, camera_y = camera.position

		# percentages start at top left
		percent_x = ((x-camera_x)+camera.view.w/2)/camera.view.w
		percent_y = abs((y-camera_y)-camera.view.h/2)/camera.view.h

		new_x, new_y = percent_x*fit_rect.w+fit_rect.x, percent_y*fit_rect.h+fit_rect.y

		camera.background.scale = float(fit_rect.w)/camera.view.w

		return (new_x, new_y)

	def init(self, **kwargs):
		_pygame.init()
		super(Graphics2D, self).init(**kwargs)

	def __init__(self, size):
		super(Graphics2D, self).__init__()
		# Layered dirty is an efficient way to do graphics.
		self.clock = _pygame.time.Clock()
		self._sprites = _pygame.sprite.OrderedUpdates()
		self._camera = Camera2D(size)
		self._cameras = [self.camera]
		self.camera._id = 0
		self._events_internal = []
		self._resize_flag = True

		_pygame.init()

	def set_caption(self, title, icontitle=None):
		"""Set the current window caption"""
		if icontitle:
			_pygame.display.set_caption(title, icontitle)
		else:
			_pygame.display.set_caption(title)

	@property
	def components(self):
		"""
		@rtype set
		@return components in the graphics
		"""
		return self.cameras.union(self.sprites)

	@property
	def sprites(self):
		"""
		@rtype set
		@return sprites in the graphics
		"""
		return set(self._sprites.sprites())

	@property
	def camera(self):
		return self._camera

	@camera.setter
	def camera(self, new_camera):
		assert new_camera in self.cameras
		self._camera = new_camera

	@property
	def cameras(self):
		return set(self._cameras)

	@classmethod
	def get_fit_rect(self, camera, display_rect):
		"""
		calculates the view offset and view scale
		based on the size of the current display_rect
		and the size of the current camera.
		@rtype (tuple, tuple)
		@return ((x_offset, y_offset), (width, height))
		"""
		fit_rect = _pygame.Rect((0, 0), camera.size).fit(display_rect)
		fit_rect.center = display_rect.center
		return fit_rect

	def _add_component(self, component):
		super(Graphics2D, self)._add_component(component)
		if isinstance(component, Sprite):
			self._add_sprite(component)
			if self.camera:
				component.update(self.camera)
		elif isinstance(component, Camera2D):
			self._add_camera(component)
		else:
			raise NotImplementedError("Unknown graphics component. Maybe needs implementing?")

	def _remove_component(self, component):
		super(Graphics2D, self)._remove_component(component)
		if isinstance(component, Sprite):
			self._remove_sprite(component)
		elif isinstance(component, Camera2D):
			self._remove_camera(component)
		else:
			raise NotImplementedError('Unknown graphics component. Could not remove.')

	def _add_sprite(self, sprite):
		# thankfully, this already does type checking
		self._sprites.add(sprite)

	def _add_camera(self, camera):
		"""
		Should give the camera an ID
		"""
		self._cameras.append(camera)
		# raise NotImplementedError

	def _remove_sprite(self, sprite):
		self._sprites.remove(sprite)

	def _remove_camera(self, camera):
		self._cameras.remove(camera)

	def _convert_pygame_event(self, pygame_event):
		"""
		Returns an event in standard format.
		If event is not handled, returns None.
		"""
		if pygame_event.type in self.event_map:
			name, attrs = self.event_map[pygame_event.type]
			kwargs = {}
			for attr in attrs:
				kwargs[attr] = getattr(pygame_event, attr)
			return Event(name, **kwargs)
		return None

	def update(self, display=None, fps=None, resolution=(0, 0), flags=0, depth=0, **kwargs):
		"""
		updates everything within the Graphics system

		recalculates view 

		calculates fps and displays it
		"""
		# if camera has changed, check it.
		# self.handle_events(_pygame.event.get())
		# we need to keep passing all the args all the way down...
		if display == None: return

		self.initialize_new_components(display=display, fps=fps, resolution=resolution, 
									   flags=flags, depth=depth, **kwargs)
		self._camera.update(display)
		self._sprites.update(self._camera)
		# self.camera.capture(self._sprites)
		for pygame_event in _pygame.event.get():
			if pygame_event.type == self.VIDEORESIZE:
				self._resize_flag = True
				self.create_display(pygame_event.size, flags, depth)
			event = self._convert_pygame_event(pygame_event)
			if event:
				self.events.push(event)
		
		# raise NotImplementedError("TODO: update cameras")

	def display(self, display=None, fps=None, **kwargs):
		"""
		Draws the camera and sprites to the screen
		and updates the passed in display.

		And for some reason, we also tick the clock here.
		This seems really bad all of a sudden.
		"""
		if display == None: return
		
		if fps and fps > 0: 
			self.clock.tick(fps)
		display.fill((0, 0, 0))
		self._camera.draw(display)
		self._sprites.draw(display)
		_pygame.display.update()



def load_image(image_file):
	return _pygame.image.load(image_file)

class Sprite2D(_pygame.sprite.DirtySprite, Sprite):
	"""
	Sprites are essentially rectangles with graphics drawn onto them.
	Creating a sprite to render a graphic allows the renderer to efficiently
	group the sprites together and draw them quickly (yet roughly).
	"""
	def __init__(self, image, offset=(0, 0), colorkey=(0, 0, 0)):
		super(Sprite2D, self).__init__()
		Sprite.__init__(self)

		self._color = (255, 255, 255)
		self._scale = 1
		self._angle = 0

		self._base_image = image.copy()
		self._colored_image = image.copy()
		self._colored_image.set_colorkey(colorkey)
		self._image = image.copy()
		self.rect = image.get_rect()

		self._basearray = _pygame.surfarray.pixels3d(self._base_image)
		self._colorarray = _pygame.surfarray.pixels3d(self._colored_image)

		self.color_image(*self._color)

		
		self.offset = offset
	
		self.rect.center = (0, 0)
		self.dirty = 1

	@property
	def image(self):
		return self._image

	@image.setter
	def image(self, new_image):
		self._image = new_image
		self.rect = new_image.get_rect()

	@property
	def color(self):
		return self._color

	@property
	def angle(self):
		return self._angle

	@angle.setter
	def angle(self, new_angle):
		if new_angle != self.angle:
			self.image = _pygame.transform.rotozoom(self._colored_image, new_angle, self.scale)
			self.image.set_colorkey((0, 0, 0))
			self.rect = self.image.get_rect()
			self.rect.center = self.position
			self._angle = new_angle
			self.dirty = True

	@property
	def scale(self):
		return self._scale

	@scale.setter
	def scale(self, new_scale):
		if new_scale != self.scale:
			self.image = _pygame.transform.rotozoom(self._colored_image, self.angle, new_scale)
			self.image.set_colorkey((0, 0, 0))
			self.rect = self.image.get_rect()
			self.rect.center = self.position
			self._scale = new_scale
			self.dirty = True

	@property
	def position(self):
		return self.rect.center

	@position.setter
	def position(self, new_position):
		x, y = new_position
		if (int(x), int(y)) != self.position:
			self.rect.center = (x, y)
			self.dirty = True

	def reset_scale_and_rotation(self):
		self.image = _pygame.transform.rotozoom(self._colored_image, self.angle, self.scale)
		self.image.set_colorkey((0, 0, 0))
		self.rect = self.image.get_rect()
		self.rect.center = self.position
		self.dirty = True

	def color_image(self, red, green, blue):
		"""
		RGB between 0-1, or 0-255: Sets the red, green, blue 
		colors of the image by the factors provided
		"""

		if type(red) == int and type(green) == int and type(blue) == int:
			# convert colors to correct format, if necessary
			red = red/255.
			green = green/255.
			blue = blue/255.
			
		assert red >=0 and red <= 1, "Invalid color value"
		assert green >=0 and green <= 1, "Invalid color value"
		assert blue >=0 and blue <= 1, "Invalid color value"
			
		self._colorarray[:,:,0] = [[int(red*c) for c in a] for a in self._basearray[:,:,0]]
		self._colorarray[:,:,1] = [[int(green*c) for c in a] for a in self._basearray[:,:,1]]
		self._colorarray[:,:,2] = [[int(blue*c) for c in a] for a in self._basearray[:,:,2]]

		self._color = (red, green, blue)
		self._colored_image.copy()
		self.reset_scale_and_rotation()

	def init(self, display=None, **kwargs):
		"""
		Should be used to initialize the graphics 
		of the sprite, in the same way that the
		Graphics system initializes displays.

		For instance, its image is 'converted' to
		turn disable alpha to speed up blitting.

		The reason to do this is because the display
		needs to be initialized in order to convert
		images. 
		"""
		if display == None: return

		self.image = self.image.convert()

	def update(self, camera=None):
		"""
		Matches the position of the sprite to the associated body.

		If no body is attached, just moves it to the appropriate offset.

		The object is then rotated by self.angle around the (0, 0) relative to the offset.
		"""
		assert camera != None
		w, h = camera.size
		c_x, c_y = camera.position
		d_x, d_y = c_x-w/2, c_y+h/2
		s_x, s_y = self.position

		if hasattr(self.parent, 'body') and self.parent.body != None:
			body = self.parent.body
			self.position = self.system.__class__.convert(body.position, _pygame.display, camera)
			self.scale = camera.background.scale
			self.angle = body.angle

		self.dirty = True


class RectSprite2D(Sprite2D):
	"""
	A primitive sprite class for drawing a rectangle.
	"""
	def __init__(self, size, offset=(0, 0), color='white'):
		square = _pygame.Surface(size)
		square.fill(_pygame.Color(color))
		
		super(RectSprite2D, self).__init__(square, offset)

class CircleSprite2D(Sprite2D):
	"""
	A primitive sprite class for drawing a Circles.
	"""
	def __init__(self, radius, line_width=0, offset=(0, 0), color='white'):
		circle = _pygame.Surface((radius*2, )*2)
		_pygame.draw.circle(circle, _pygame.Color(color), [radius]*2, radius, line_width)
		
		super(CircleSprite2D, self).__init__(circle, offset)

class LineSegment(Sprite2D):
	def __init__(self, a, b, radius, offset=(0, 0), color='white'):
		(x1, x2), (y1, y2) = zip(a, b)
		line = _pygame.Surface((abs(x2-x1)+1, abs(y2-y1)+1))
		_pygame.draw.line(line, _pygame.Color(color), a, b, radius)

		super(LineSegment, self).__init__(line, offset)

class PolySprite2D(Sprite2D):
	def __init__(self, vertices, line_width=0, offset=(0, 0), color='white'):
		min_x, min_y, max_x, max_y = float('inf'), float('inf'), -float('inf'), -float('inf')
		for x, y in vertices:
			min_x = min(min_x, x)
			min_y = min(min_y, y)
			max_x = max(max_x, x)
			max_y = max(max_y, y)
		vertices = [(x-min_x, y-min_y) for x, y in vertices]
		width = max_x - min_x
		height = max_y - min_y
		center = (max_x+min_x)/2, (max_y+min_y)/2
		poly = _pygame.Surface((width, height))
		_pygame.draw.polygon(poly, _pygame.Color(color), vertices)
		
		super(PolySprite2D, self).__init__(poly, offset)
		
		self.position = center

# A special kind of sprite that is used to actually draw things to the display.
class Camera2D(_GraphicsComponent):
	""" Used as the view port. 
	Keeps tracks of the spites within view 
	of the camera and uses that to render 
	to its display.

	'Within sight of the camera' is partly 
	determined by the physics. Imagine a rectangle 
	that floats around in the physics space. 
	Things are then blitted onto than surface. 
	The surface is then scaled to fit the display.

	The job of the Camera is to draw sprites
	onto a surface which should then be
	drawn to the display itself.

	Can be moved around by changing its position.

	Should be able to attach to a game object (or body)
	to follow.

	TODO
	Should be able to adjust the way it follows: 
	- only moves when object moves a certain amount
	- get pulled around by object like a gliding effect
	- stops when hits edge of map (need to defineedge of map).)
	"""
	# angle = 0 Not sure how to adjust angle
	name = "camera"
	def __init__(self, size, background_color='black'):
		"""
		The size of the camera display defaults to a known maximum.
		Setting the camera size will set the aspect ratio.
		"""
		super(Camera2D, self).__init__()

		self.view = _pygame.Rect((0, 0), size)
		self.scale = 1
		self.angle = 0
		self.position = (0, 0)

		self.background = RectSprite2D(size, color=background_color)

	@property
	def size(self):
		return self.view.size

	@size.setter
	def size(self, new_size):
		self.view.size = new_size

	@property
	def background_color(self):
		return self._background_color

	@background_color.setter
	def background_color(self, new_color):
		self._background_color = new_color
		self.background.color_image(*new_color)

	def update(self, display=None, **kwargs):
		# Sprite2D.update(self) # should be used to update body.

		"""
		this should also update to see what sprites
		are within view of the camera


		"""
		if display == None: return

		display_rect = display.get_rect()
		fit_rect = self.view.fit(display_rect)
		fit_rect.center = display_rect.center
		self.background.scale = fit_rect.width/float(self.view.width)
		# self.scale = self.fit_rect.width/float(self.size[0])

	def draw(self, display):
		display_rect = display.get_rect()
		fit_rect = self.view.fit(display_rect)		
		display.blit(self.background.image, fit_rect)
		fit_rect.center = display_rect.center
		return [fit_rect]
		# raise NotImplementedError('Need to move camera around?')

	def fit(self, sprites):
		"""
		Adjusts the view's size to 
		make all the sprites visible.

		Sprites can be any collection of sprites,
		lists of sprites, or sprite groups. 

		This seems like a stretch of a function...
		"""
		if not len(sprites):
			return 
		min_x = 0
		max_x = 0
		min_y = 0
		max_y = 0

		co_x = 0
		co_y = 0
		for sprite in sprites:
			x, y = sprite.position
			w, h = sprite.rect.size

			
			min_x = min(min_x, x-w/2)
			max_x = max(max_x, x+w/2)

			min_y = min(min_y, y-h/2)
			max_y = max(max_y, y+h/2)

		new_w = max_x-min_x
		new_h = max_y-min_y

		new_x = (max_x+min_x)/2
		new_y = (max_y+min_y)/2

		self.size = (new_w, new_h)
		self.position = (new_x, new_y)
		return new_x, new_y, new_w, new_h

	def zoom(self, zoom_factor):
		"""
		changes the size of the view 
		maintaining aspect ratio. 

		a zoom_factor of 2 will halve 
		the 'size' of the view.

		in this case, 
		"""
		w, h = self.size
		self.size = (w*zoom_factor, h*zoom_factor)
		# raise NotImplementedError

	# def capture(self, sprites):
	# 	"""
	# 	clears the current view,
	# 	takes all the sprites intersecting 
	# 	with the view and draws it to the view.

	# 	Need to iterate over the sprites to display,
	# 	and position them correctly to draw.
	# 	"""
	# 	self.view.blit(self.background, (0, 0))
	# 	# sprites.draw(self.view)
	# 	w, h = self.size
	# 	c_x, c_y = self.position
	# 	d_x, d_y = c_x-w/2, c_y+h/2
	# 	for sprite in sprites:
	# 		s_x, s_y = sprite.position
	# 		# sprite.rect.center = s_x-d_x, d_y-s_y
	# 		img = _pygame.transform.rotozoom(sprite.image, sprite.angle, sprite.scale)
	# 		rect = img.get_rect()
	# 		rect.center = s_x-d_x, d_y-s_y
	# 		img.set_colorkey((0, 0, 0))
	# 		self.view.blit(img, rect)

class Graphics2DGrid(Graphics2D):
	pass

class Sprite2DGrid(Sprite2D):
	def __init__(self, image):
		super(Sprite2DGrid, self).__init__(image, offset=(0, 0))

	@property
	def offset(self):
		return (0, 0)

	def update(self, **kwargs):
		if hasattr(self.parent, 'body'):
			body = self.parent.body
			print body.position
			# self.position = body.position


class RectSprite2DGrid(RectSprite2D):
	def __init__(self):
		super(RectSprite2DGrid, self).__init__((1, 1))


if __name__ == '__main__':

	system_graphics = Graphics2D((800, 800))
	sprite = RectSprite2DGrid()
	system_graphics._add_sprite(sprite)

	system_graphics.init()
	system_graphics.update()
	system_graphics.display()
