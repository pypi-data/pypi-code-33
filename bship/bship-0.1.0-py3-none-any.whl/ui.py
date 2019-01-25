import sys
from random import randint, choice
from battleship.config import PROMPT


def show_board(one_brd):
    """Takes the player's Board and displays it with Board's __str__.
    """
    print("\n\t*Player1 Board")
    print(one_brd.__str__() + '\n')


def show_game(one_brd, comp_brd):
    """Takes the player's Board and displays it with Board's __str__ takes
    computer's Board and displays the board without revealing ship location.
    """
    print("\t*ATTACK")  # the computer's board
    print(comp_brd.__str__(True))  # ships hide=True
    print("\t*DEFEND")  # the player's board
    print(one_brd.__str__())


def flip():
    """Decide who goes first.
    """
    coin = {'H': 'HEADS', 'T': 'TAILS', '': 'HEADS'}

    for n in range(3):
        try:
            call = coin[input(PROMPT['call_coin']).upper()]
            break
        except KeyError:
            print(PROMPT['just_call'])
    else:
        print(PROMPT['comp_first'])
        return None

    flip = choice(['HEADS', 'TAILS'])

    print(PROMPT['flip_coin'].format(call, flip))

    if call == flip:
        print(PROMPT['one_first'])
        return True
    else:
        print(PROMPT['comp_first'])
        return None


def to_quit():
    """After failed attempts, prompts the user whether to quit.
    """
    ans = input(PROMPT['quitter'])

    if ans == '':
        sys.exit()
    elif ans[0].lower() == 'n':
        return None
    else:
        sys.exit()


def clean(entry):
    """Parses user input mostly will convert user input to a two character
    ALPHAdigit string.
    """
    # special case of being able to quit
    if entry.lower() == 'q':
        to_quit()
    # special case of relocating head coord if user dislikes tail options
    elif entry.lower() == 'r':
        return entry.lower()

    # normal case returns LETTERnumber
    for p in ",./'(){}[]\" ":
        entry = entry.replace(p, '')

    if len(entry) == 2 and entry[0].isalpha() and entry[1].isdigit():
        return entry.upper()
    else:
        return None


def convert(coord):
    """Converts coordinate as displayed coordinates to digit tuple eg: J9 ->
    (9,9); checks for possible human errors converts coordinate as digit tuple
    to displayed coordinates eg: (0,0) -> A0; should not have any errors.
    """
    # dictionary to convert letter coordinate to numbers for row coordinates
    A2D = dict(zip('ABCDEFGHIJ', range(10)))
    # vice-a-versa
    D2A = dict(zip(range(10), 'ABCDEFGHIJ'))

    if isinstance(coord, str):
        try:
            coord = A2D[coord[0]], int(coord[1])
            if 0 <= coord[1] < 10:
                return coord
            else:
                return None  # reject if row not in range(10)
        except KeyError:
            return None  # reject if col not in 'ABCDEFGHIJ'
    else:
        coord = D2A[coord[0]] + str(coord[1])
        return coord


def pick_coord(ask):
    """Prompts the user to select a coordinate; takes a string parameter to
    specify a prompt uses clean() and convert() to validate input returns valid
    coord entry returns None for invalid input.
    """
    for n in range(5):
        coord = clean(input(PROMPT[ask]))

        if not coord:
            print(PROMPT['bad_coord'].format(
                convert((randint(0, 9), randint(0, 9)))))
            continue
        # special case: relocating head coord if user dislikes tail options
        if ask == 'hide_tail' and coord == 'r':
            return coord

        new = convert(coord)
        if new:
            return new
        else:
            print(PROMPT['off_board'])
            continue
    else:
        to_quit()
