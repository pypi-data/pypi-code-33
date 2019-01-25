from battleship.config import POINT
from battleship.ship import Ship


class Board(object):

    def __init__(self, rows=10, cols=10):
        """Creates a new board dataset: tuple as key dictionary with each coord
        as open/miss/occupied/hit/sunk status O X K @ k number of row/column
        maximum of 10 otherwise players.pick_pos will not work.
        Initialises a fleet of ships.
        """
        self.board = {}
        self.rows = rows
        self.cols = cols

        for row in range(rows):
            for col in range(cols):
                self.board[(col, row)] = POINT['open']

        self.fleet = {
            'K': Ship('AircraftCarrier', 'K', 5),
            'T': Ship('Battleship', 'T', 4),
            'S': Ship('Submarine', 'S', 3),
            'Y': Ship('Destroyer', 'Y', 3),
            'P': Ship('PatrolBoat', 'P', 2)
        }

    def __str__(self, hide=False):
        """Converts board dict tuple as key into a list of list to display. It
        will or will not display ships depending on the `hide` parameter.
        """
        str_board = []  # will become a list containing str_row lists
        # the column reference row is being made first
        str_row = ['+']
        for col in 'ABCDEFGHIJ'[:self.cols]:
            str_row.append(f'  {col}')

        # the col_ref row is appended to the str_board list
        # and elements of str_row joined into a string)
        str_board.append(f'\t{"".join(str_row)}')

        for row in range(self.rows):
            str_row = []
            for col in range(self.cols):
                if hide and self.board[(col, row)] in self.fleet.keys():
                    str_row.append(f' {POINT["open"]} ')
                else:
                    str_row.append(f' {self.board[(col, row)]} ')

            str_board.append(f'\t{row} {"".join(str_row)}')

        return '\n'.join(str_board)

    def place_ship(self, ship, pos):
        """Record the ship's pos and place a ship on the board.
        Eg. change O to S or P etc.
        """
        ship.pos = pos
        for coord in ship.pos:
            self.board[coord] = ship.sign

    def remove_ship(self, ship):
        """Remove a ship ie. change K or T etc. back to O and delete the ship's
        position.
        """
        for coord in ship.pos:
            self.board[coord] = POINT['open']
        ship.empty()

    def remove_fleet(self):
        """Removes a fleet of ships from the board and deletes each Ship's
        position.
        """
        for ship in self.fleet:
            self.remove_ship(self.fleet[ship])

    def record_miss(self, coord):
        """Changes the point representation of the coord to a miss.
        """
        self.board[coord] = POINT['miss']

    def record_hit(self, coord):
        """Changes the point representation of the coord to a hit.
        """
        self.board[coord] = POINT['hit']

    def record_sunk(self, ship):
        """Changes the point representation of the list of coords to a sunk.
        """
        for coord in ship.pos:
            self.board[coord] = ship.sign.lower()
