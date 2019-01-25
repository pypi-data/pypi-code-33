import random
from battleship.players import Human, Computer
from battleship.config import PROMPT
from battleship.ui import show_game, convert, flip


class Engine(object):

    def __init__(self):
        """Engine has a list of players.
        """
        self.opponent = Computer()
        self.home = Human()
        self.players = self.opponent, self.home

    def start(self):
        """Starts the game with some instructions.
        """
        print(PROMPT['title'])
        print(PROMPT['explain'])

        self._example_setup()

        eg_ship = random.choice(list(self.opponent.brd.fleet.values()))

        print(self.opponent.brd)

        print(PROMPT['example'].format(eg_ship, convert(eg_ship.pos[0]),
                                       convert(eg_ship.pos[-1])))

        self.opponent.brd.remove_fleet()

        input(PROMPT['ready'])

    def set(self):
        """Set up each player's board, and decides who goes first with flip().
        """
        for player in self.players:
            player.set_up()

        if flip():
            self.current_player = self.home
            self.next_player = self.opponent
        else:
            self.current_player = self.opponent
            self.next_player = self.home

        input(PROMPT['comprehend'])

    def play(self):
        """Rolls out the turns, determines who wins.
        """
        turn = 0
        first2go = self.current_player

        print(PROMPT['turn_line'].format(turn))

        show_game(self.home.brd, self.opponent.brd)

        while True:
            if self.current_player == first2go:
                turn += 1
                print(PROMPT['turn_line'].format(turn))

            point = self.current_player.where2bomb()
            self.next_player.receive_shot(point)

            if self.current_player != first2go:
                show_game(self.home.brd, self.opponent.brd)
                input(PROMPT['comprehend'])

            if self.next_player.sunk == 5:
                return self.current_player.win()

            self.current_player, self.next_player =\
                self.next_player, self.current_player

    def end(self):
        """Asks whether to play again or not.
        """
        again = input(PROMPT['play_again']).lower()

        if again == 'n' or again == 'no':
            return None
        else:
            return True

    def _example_setup(self):
        """Setup to show an example of the board and game.
        """
        fleet = self.opponent.brd.fleet
        fleet_lst = [fleet[ship] for ship in fleet]
        random.shuffle(fleet_lst)

        for ship in fleet_lst:
            self.opponent.auto_hide_ships(ship, 2)
