from battleship.ship import Ship

PROMPT = {
    # .engine
    'title': "\n\t    **BATTLESHIPS**\n",
    'explain': """   Battleships is a two player guessing game.
       Each player hides five ships, and takes turns to guess
       the coordinates of their enemy's ships.
       The first player to sink all five enemy ships is the winner.\n""",
    'example': """\n   The ships are labelled as Sign Name(Size).
       for example: {} has head coordinate {}
       and tail coordinate {}.""",
    'ready': "\nReady to play? >> ",
    'border': "\n   ===============*Hide Ships*================",
    'turn_line': "\n   ===============* Battle {} *==================",
    'which_ship': "Which ship do you want to hide?\n   {}\t(Type the sign of \
a ship or type 'A' to autohide.)\n>> ",
    'which_ship_explain': "To hide a ship type one of these letters: {}.\n",
    'good2go': "Are you good with this board?\n([Y]/n) >> ",
    'start_again': "OK let's reset the board...",
    'call_coin': "To decide who goes first, Computer will flip a coin. Heads \
or Tails??\n([h]/t) >> ",
    'just_call': "It's quite easy, just type  h  or  t.",
    'flip_coin': "Player calls {}, the coin flips.... {}",
    'one_first': "Player gets to go first!",
    'comp_first': "Computer will go first.",
    'result': "\n   ===============** result **===================",
    'one_wins': "\n   Player1 wins!\n",
    'comp_wins': "\n   Computer wins!\n",
    'comprehend': ">>",
    'play_again': "Do you want to play again??\n >> ",
    # .players
    'miss': "   MISS!",
    'already_shot': "   You've already shot here, what a waste!",
    'already_sunk': "   You've already sunk a ship here, what a waste!",
    'sunk': "   And sinks the enemy {}!",
    'hit': "   And hits the enemy {}.",
    'bad_coord': "Type a coordinate LETTERnumber eg. {}",
    'off_board': "Your coordinate missed the sea. Try again.",
    'where2bomb': "Which coordinate do you want to bomb??\n>> ",
    'lets_hide': "Let's hide the {}.",
    'player_hidden': "   Player1 has hidden the {}",
    'comp_hidden': "   Computer has hidden the {}",
    'hide_head': "Which coordinate do you want to hide the head of the \
ship??\n>> ",
    'hide_tail': "Pick a coordinate for the tail of the ship (or type 'R' to \
relocate head coord).\n>> ",
    'tail_option': "The tail of the ship can be hidden in these \
coordinates:\n\t {} ",
    'revise': "Or did you want to change the head coordinate of the \
ship??\n(Y/n) >> ",
    'wrong_tail': "You will have to hide the ship with a new head \
coordinate...",
    'occupied': "These coordinates are already occupied by another ship of \
your fleet.",
    'no_tail': "For this head coordinate, there are no possible tail \
coordinates. Choose another head coordinate.",
    'this_tail_ok': "The tail of the ship can be hidden in this \
coordinate:\n\t{}\n([Y]/n) >> ",
    'quitter': "Are you bored... do you want to quit??\n([Y]/n) >> ",
    'pos_ok?': "The {} will be hidden here:\n\t[ {} ]\n([Y]/n) >> ",
    'player_attack': "Player1 attacks {}.",
    'comp_attack': "Computer attacks {}.",
    'bored': "OK you're bored, Goodbye!!"
}

POINT = {
    'open': '.',
    'miss': 'x',
    'hit': '@'
}

FLEET = {
    'K': Ship('AircraftCarrier', 'K', 5),
    'T': Ship('Battleship', 'T', 4),
    'S': Ship('Submarine', 'S', 3),
    'Y': Ship('Destroyer', 'Y', 3),
    'P': Ship('PatrolBoat', 'P', 2)
}
