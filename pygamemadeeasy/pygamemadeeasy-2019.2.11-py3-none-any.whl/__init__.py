import pygame
import time
import random
import pygamemadeeasy.colors as colors
import pygamemadeeasy.keys as keys
from pygame.locals import *

"""
Requires:
 * Python 3.6 minimum (remove use of f-strings if you need to customise for an earlier version of Python 3)
"""

class UI():
    """ User-interface data to pass via the callback """
    def __init__(self):
        self.x = 0
        self.y = 0
        self.click = False
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.space = False
        self.ctrl = False
        self.alt = False
        self.shift = False
        self.enter = False
        self.keyspressed = []
    
    def __str__(self):
        return str(f"pos=({self.x},{self.y}), button={self.click}, keys={self.keyspressed}")
    
    def __contains__(self, item):
        return item in self.keyspressed

    def _key_down(self, key):
        if key in keys.all and keys.all[key] not in self.keyspressed:
            self.keyspressed.append(keys.all[key])
        if key == K_LEFT: self.left = True
        if key == K_RIGHT: self.right = True
        if key == K_UP: self.up = True
        if key == K_DOWN: self.down = True
        if key == K_SPACE: self.space = True
        if key == K_LSHIFT or key == K_RSHIFT: self.shift = True
        if key == K_LALT or key == K_RALT: self.alt = True
        if key == K_LCTRL or key == K_RCTRL: self.shift = True
        if key == K_RETURN: self.enter = True
    
    def _key_up(self, key):
        if key in keys.all and keys.all[key] in self.keyspressed:
            self.keyspressed.remove(keys.all[key])
        if key == K_LEFT: self.left = False
        if key == K_RIGHT: self.right = False
        if key == K_UP: self.up = False
        if key == K_DOWN: self.down = False
        if key == K_SPACE: self.space = False
        if key == K_LSHIFT or key == K_RSHIFT: self.shift = False
        if key == K_LALT or key == K_RALT: self.alt = False
        if key == K_LCTRL or key == K_RCTRL: self.shift = False
        if key == K_RETURN: self.enter = False
    
    def is_keypressed(self, key):
        return key in self.keyspressed

    def get_keyspressed(self):
        return self.keyspressed

class PygameMadeEasy():
    def __init__(self, width, height):
        """ 
        PygameMadeEasy constructor
        Parameters: width, height: pixel dimensions for window to open on screen
        """ 
        self.width = width
        self.height = height
        self.framerate = 25
        self.clear_every_frame = True
        self.background = colors.black
        self.fill = colors.white
        self.stroke = colors.white
        self.console_events = False
        self.images = {}                # maps filenames to loaded image binaries (as a cache to avoid reloading in the game loop)
        self.sounds = {}                # maps filenames to loaded sound binaries (as a cache to avoid reloading in the game loop)
        self.image_animations = {}      # current frame number of the sprite we are displaying
    
    def set_fill(self, color):
        """ Set the fill color. Common colors available in pygamemadeeasy.colors """
        self.fill = color

    def set_stroke(self, color):
        """ Set the stroke color. Common colors available in pygamemadeeasy.colors """
        self.stroke = color

    def set_background(self, color):
        """ Set the background color. Common colors available in pygamemadeeasy.colors """
        self.background = color

    def circle(self, x, y, radius, borderwidth=0):
        # Set colour
        c = self.fill
        if borderwidth > 0:
            c = self.stroke
        # Draw circle
        pygame.draw.circle(self.window, c, (x,y), radius, borderwidth)
        return Rect(x-radius, y-radius, radius*2, radius*2)

    def line(self, x, y, x2=None, y2=None, w=None, h=None, borderwidth=1):
        if x2 is not None and y2 is not None:
            pygame.draw.line(self.window, self.stroke, (x,y), (x2,y2), borderwidth)
        elif w is not None and h is not None:
            pygame.draw.line(self.window, self.stroke, (x,y), (x+w,y+h), borderwidth)

    def rectangle(self, x, y, x2=None, y2=None, w=None, h=None, borderwidth=0):
        c = self.fill
        if borderwidth > 0:
            c = self.stroke
        if x2 is not None and y2 is not None:
            pygame.draw.rect(self.window, c, Rect(x,y,x+w,y+h), borderwidth)
            return Rect(x,y,x+w,y+h)
        elif w is not None and h is not None:
            pygame.draw.rect(self.window, c, Rect(x,y,w,h), borderwidth)
            return Rect(x,y,w,h)

    def rect(self, rectangle, borderwidth=0):
        c = self.fill
        if borderwidth > 0:
            c = self.stroke
        if isinstance(rectangle, pygame.Rect):
            pygame.draw.rect(self.window, c, rectangle, borderwidth)

    def polygon(self, coordinates, borderwidth=0):
        c = self.fill
        if borderwidth > 0:
            c = self.stroke
        pygame.draw.polygon(self.window, c, coordinates, borderwidth)

    def image(self, x, y, filename, rotate=0):
        """
        - rotate: (optional) angle in degrees to rotate counter-clockwise
        """
        if filename not in self.images:
            try:
                self.images[filename] = pygame.image.load(filename).convert_alpha()
            except:
                exit("[pygamemadeeasy] Unable to find or load file: "+filename)
        im = self.images[filename]
        if rotate != 0:
            im = pygame.transform.rotate(self.images[filename], rotate)
        self.window.blit(im, (x, y))
        return Rect(x, y, im.get_width(), im.get_height())
    
    def image_piskel_animation(self, x, y, filename, cell_width, cell_height, rotate=0):
        """
        Will automatically create an animated sprite for images exported from piskelapp.com, or other compatible image. 
        Image will be assumed to be 1 column by multiple rows of frames (the default "export to PNG" settings of Piskelapp)
        Parameters:
        - filename: path to the image file
        - cell_width: width in pixels of each individual frame
        - cell_height: height in pixels of each individual frame
        - rotate: (optional) angle in degrees to rotate counter-clockwise
        """
        if filename not in self.images:
            try:
                self.images[filename] = pygame.image.load(filename).convert_alpha()
                self.image_animations[filename] = { "current_frame": 0 }
            except:
                exit("[pygamemadeeasy] Unable to find or load file: "+filename)
        # calculations
        current_frame = self.image_animations[filename]["current_frame"]
        total_height = self.images[filename].get_height()
        total_rows = total_height // cell_height
        from_y = current_frame * cell_height
        from_x = 0
        # draw the sprite onto screen
        if rotate == 0:
            self.window.blit(self.images[filename], (x, y), (from_x, from_y, cell_width, cell_height))
        else:
            im = pygame.Surface((cell_width,cell_height), pygame.SRCALPHA).convert_alpha()
            im.blit(self.images[filename], (0, 0), (from_x, from_y, cell_width, cell_height))
            self.window.blit(pygame.transform.rotate(im, rotate), (x, y))
        # increment the frame counter for the next iteration
        current_frame += 1
        if current_frame >= total_rows:
            current_frame = 0
        self.image_animations[filename]["current_frame"] = current_frame
        return Rect(x, y, cell_width, cell_height)

    def text(self, x, y, message, size=12, font="Arial" ):
        pygame_font = pygame.font.SysFont(font, size)
        text_image = pygame_font.render(message, 1, self.stroke)
        self.window.blit(text_image, (x, y))

    def music(self, mp3_filename, loop=True):
        try:
            pygame.mixer.music.load(mp3_filename)
            if loop:
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.play(0)
        except:
            exit("[pygamemadeeasy] Unable to find or load file: "+mp3_filename)

    def sound(self, wav_filename):
        if wav_filename not in self.sounds:
            try:
                self.sounds[wav_filename] = pygame.mixer.Sound(wav_filename)
            except:
                exit("[pygamemadeeasy] Unable to find or load file: "+wav_filename)
        self.sounds[wav_filename].play()

    def get_pixel(self, x, y):
        return self.window.get_at(( x , y ))
    
    def get_distance_between_points(self, x1, y1, x2, y2):
        dx = abs(x2-x1)                     # difference in x values
        dy = abs(y2-y1)                     # difference in y values
        return int((dx**2 + dy**2)**0.5)    # distance is hypotenuse of pythagoras
    
    def is_collision(self, box1, box2):
        if isinstance(box1, Rect) and isinstance(box2, Rect):
            return box1.colliderect(box2)
        else:
            raise Exception("[pygamemadeeasy] is_collision must be passed two box rectangles (Pygame Rect) objects")

    def play(self, loop, keydown=None, keyup=None, mousemotion=None, mousebutton=None):
        """
        Start main game play loop.
        Parameters:
        loop: function containg your game logic. Will be executed 25 times per second. If the function returns False, the game will quit. Will pass a UI object and the pygame window as parameters.
        keydown: (optional) funciton to call when a key is initially pressed down.  Will pass the character value as a string parameter.
        keyup: (optional) function to call when a key is released. Will pass the character value as a string parameter.
        mousemotion: (optional) function to call anytime the mouse is moved. Will pass the mouse-x and mouse-y coordinates as two integer parameters.
        mousebutton: (optional) function to call when the main mouse button is clicked. Will pass the mouse-x and mouse-y coordinates as two integer parameters.
        """
        ui = UI()
        pygame.init()                                               # Initialise pygame
        self.window = pygame.display.set_mode((self.width,self.height))
        self.fps = pygame.time.Clock()
        self.running = True
        while self.running:                                         # Main game loop
            for event in pygame.event.get():                        # Process events received since previous frame
                if self.console_events:
                    print(event)
                if event.type == pygame.locals.QUIT:                # Exit on click of the window close icon
                    self.running = False
                elif event.type == pygame.locals.KEYDOWN:
                    if event.key == pygame.locals.K_ESCAPE:         # Exit on press of the Escape key
                        self.running = False
                    else:
                        ui._key_down(event.key)
                        if callable(keydown) and event.key in keys.all:
                            keydown(keys.all[event.key])
                elif event.type == pygame.locals.KEYUP:
                    ui._key_up(event.key)
                    if callable(keyup) and event.key in keys.all:
                        keyup(keys.all[event.key])
                elif event.type == pygame.locals.MOUSEMOTION:
                    ui.x = event.pos[0]
                    ui.y = event.pos[1]
                    if callable(mousemotion):
                        mousemotion(event.pos[0], event.pos[1])
                elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        ui.x = event.pos[0]
                        ui.y = event.pos[1]
                        ui.click = True
                        if callable(mousebutton):
                            mousebutton(event.pos[0], event.pos[1])
                elif event.type == pygame.locals.MOUSEBUTTONUP:
                    if event.button == 1:
                        ui.click = False

            if self.clear_every_frame:                              # Reset the screen window content each loop by default
                self.window.fill(self.background)
            
            if callable(loop):                                      # Run the game logic callback
                ret = loop(ui, self.window)
                if ret is not None and isinstance(ret, bool) and not(ret):
                    self.running = False                            # If the callback explicitly returns a False boolean value, quit the game
            pygame.display.update()                                 # Update screen window and complete frame clock tick
            self.fps.tick(self.framerate)
        pygame.quit()                                               # Exit pygame

class SpriteAnimation():
    def __init__(self, filename, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.current_frame = 0
        self.image = pygame.image.load(filename).convert_alpha()
    
    def goto_frame(self, frame_number, rotate=0):
        self.current_frame = frame_number
        return self.next_frame(rotate)

    def next_frame(self, rotate=0):
        # calculations
        total_width = self.image.get_width()
        total_height = self.image.get_height()
        total_cols = total_width // self.frame_width
        total_rows = total_height // self.frame_height
        total_frames = total_cols * total_rows
        current_row = self.current_frame // total_cols
        current_col = self.current_frame - current_row*total_cols
        from_x = current_col * self.frame_width
        from_y = current_row * self.frame_height
        # print(f"frame {self.current_frame} total_cols {total_cols} total_rows {total_rows} current_col {current_col} current_row {current_row} from_x {from_x:2} from_y {from_y:2}")
        # draw the sprite onto screen
        im = pygame.Surface((self.frame_width,self.frame_height), pygame.SRCALPHA).convert_alpha()
        im.blit(self.image, (0, 0), (from_x, from_y, self.frame_width, self.frame_height))
        if rotate != 0:
            im = pygame.transform.rotate(im, rotate)
        # increment the frame counter for the next iteration
        self.current_frame += 1
        if self.current_frame >= total_frames:
            self.current_frame = 0
        return im

### The end
