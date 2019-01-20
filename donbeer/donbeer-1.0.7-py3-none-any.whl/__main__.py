from threading import Thread
import pygame

from donbeer.beer import Beer
from donbeer.configuration import Configuration
from donbeer.donut import Donut
from donbeer.game import Game
from donbeer.text import Text
from pkg_resources import resource_stream, resource_filename

FPS = 60
LIGHTBLUE = (131, 66, 244)
CYAN = (0, 255, 255)


def main():
    """Run the game and create/configure main-elements"""

    beer = Beer(resource_stream(__name__, 'resources/images/beer2.png'))
    donut = Donut(0, resource_stream(__name__, 'resources/images/donut2.png'))
    game = Game(Configuration(700, 600, LIGHTBLUE), 60)
    game.config.set_up(True)

    for element in [donut, beer]:
        element.rect.center = (game.config.window.get_width() / 2, game.config.window.get_height() / 2)

    game.new_round(beer)

    setup_texts(game)

    thread = Thread(target=game.countdown)
    thread.start()
    while True:  # main game loop
        # Set the data for Points and Countdown
        game.handle_input()
        game.handle_event(beer, donut)

        game.config.window.fill(LIGHTBLUE)
        if game.new_game:
            break

        if game.is_finished:
            game.show_text('result', game.points)
            game.show_text('restart')

        else:
            if game.get_status(beer) == 'donut':
                game.show_game_object(donut)

            else:
                game.show_game_object(beer)

            game.show_text('points', game.points)
            game.show_text('round', game.round)
            game.show_text('time', game.game_time)
            game.show_text('instruction')

        pygame.display.update()
        game.config.fps_clock.tick(FPS)
    return 0


def setup_texts(game):
    """Add the text elements to the game object"""
    game.add_text(Text('points', resource_filename(__name__, 'resources/fonts/MeathFLF.ttf'), 60, 'Points: '))
    game.add_text(Text('round', resource_filename(__name__, 'resources/fonts/MeathFLF.ttf'), 60, 'Round: '))
    game.add_text(Text('time', resource_filename(__name__, 'resources/fonts/MeathFLF.ttf'), 60, 'Time: '))
    game.add_text(
        Text('instruction', resource_filename(__name__, 'resources/fonts/MeathFLF.ttf'), 60, 'Don\'t press the donut!'))
    game.add_text(Text('result', resource_filename(__name__, 'resources/fonts/MeathFLF.ttf'), 130, 'Total result: '))
    game.add_text(Text('restart', resource_filename(__name__, 'resources/fonts/MeathFLF.ttf'), 80, '>>>RESTART<<<'))
    set_text_coords(game)


def set_text_coords(game):
    """Set the coordinates(x,y) on the pane for the text elements"""

    window_width = game.config.window.get_width()
    window_height = game.config.window.get_height()

    game.get_text('points').set_coords(window_width / 5, window_height / 3)
    game.get_text('round').set_coords(window_width / 5, window_height / 2)
    game.get_text('time').set_coords(window_width / 4 * 3, window_height / 3)

    instruction = game.get_text('instruction')
    instruction.set_coords(window_width / 2 - instruction.label.get_width() / 2, window_height / 4)

    restart = game.get_text('restart')
    restart.set_coords(window_width / 2 - restart.label.get_width() / 2, window_height / 3 * 1.5)

    result = game.get_text('result')
    result.set_coords(window_width / 2 - result.label.get_width() / 2, window_height / 4)


if __name__ == '__main__':
    while main() == 0:
        main()
