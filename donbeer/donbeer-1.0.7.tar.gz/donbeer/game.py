import datetime
import sys
from random import randint
from time import sleep

import pygame
from pygame.locals import *


class Game:
    """
    This Class is the basic overlay of donbeer.
    It holds and handles nearly all information.
    """

    def __init__(self, config, game_time):
        self.texts = []
        self.round = 0
        self.points = 0
        self.config = config
        self.donut_wait_start = None
        self.is_finished = False
        self.game_time = game_time
        self.ran_num = None
        self.random_time = None
        self.mouse_pos = None
        self.new_game = False

    def new_round(self, beer):
        """Start a new round with random int for the donut pause"""

        self.round += 1
        self.ran_num = randint(2, 20)

        beer.clicks = 0
        self.random_time = randint(1, 5)

    def wait(self):
        """Check if the pause of the donut is over or not"""

        if self.donut_wait_start:
            # Adds seconds to the start-time and gets the end time
            donut_wait_end = self.donut_wait_start + datetime.timedelta(seconds=self.random_time)
            if datetime.datetime.now() >= donut_wait_end:
                self.donut_wait_start = None
                return False
            else:
                return True

    def get_status(self, beer):
        """Get the status, of witch item is currently displayed"""

        if beer.clicks == self.ran_num:
            self.donut_wait_start = datetime.datetime.now()
            self.new_round(beer)
            return 'donut'
        elif self.wait():
            return 'donut'
        else:
            return 'beer'

    def handle_event(self, beer, donut):
        """Handle what happens if the beer, donut or restart was clicked"""

        if self.mouse_pos is not None:
            if self.is_finished:
                # if the user clicked onto the restart text
                if Game.is_over_rect(self.get_text('restart'), self.mouse_pos):
                    self.is_finished = False
                    self.new_game = True
            else:
                # if the user clicked onto beer or donut
                if Game.is_over_rect(beer, self.mouse_pos) or Game.is_over_rect(donut, self.mouse_pos):
                    # if he has clicked in the beer phase
                    if self.get_status(beer) == 'beer':
                        beer.clicks += 1
                        self.points += beer.clicks
                    else:
                        self.is_finished = True

    def handle_input(self):
        """Set the mouse position for the users-click, or exit the game"""

        self.mouse_pos = None
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # If clicked
            if event.type == MOUSEBUTTONUP and event.button == 1:
                self.mouse_pos = pygame.mouse.get_pos()

    def show_text(self, text_name, var=None):
        """Display the the provided text (or with a variable like points) on the screen."""

        text = self.get_text(text_name)
        if var:
            text.content[1] = var
            text.set_label(True)
        else:
            text.set_label(False)
        # render text
        self.config.window.blit(text.label, (text.x, text.y))
        return text.label

    def show_game_object(self, game_object):
        """Display the provided object on the screen"""

        self.config.window.fill(self.config.color)
        self.config.window.blit(game_object.img, game_object.rect)

    @staticmethod
    def is_over_rect(game_object, mouse_pos):
        """Check if the mouse position is in the range of the provided object"""

        if game_object.rect.collidepoint(mouse_pos):
            return True
        return False

    def countdown(self):
        """Count down to 0 from the configured game time. Terminate if over."""

        while self.game_time >= 0:
            sleep(1)
            self.game_time -= 1
        self.is_finished = True

    def add_text(self, text):
        """Add the provided text object to the array of texts"""

        self.texts.append(text)

    def get_text(self, text_name):
        """Obtain the text object based upon the provided name"""

        for text in self.texts:
            if text.name == text_name:
                return text
