#!/usr/bin/env python3

__version__ = '4.0'

from operator import sub, add
import random


NIL = 0
BLIND = DOUBLE = -1

class Exit(Exception):
    pass

class Undo(Exception):
    pass

class CannotUndo(Exception):
    pass

class RequiredMethods(type):
    """Meta class that ensures classes have defined certain methods. To use,
    first define a top-level class for other classes to inherit from:

                                  # class name
                                  # ^        base classes
    >>> MyClass = RequiredMethods('MyClass', (), {
    ...     '_METHODS': {'method1', 'method2', 'method3'},
    ...     'do_check': False,
    ... })

    The last argument (False) states that this is class does not need to follow
    the rules. It is there merely to serve as a starting point for other classes.
    Now any class that inherits from MyClass will have this meta class:

    >>> class NewClass(MyClass):
    ...     def method1(self):
    ...         print("Yay!")
    ...
    Traceback (most recent call last):
      ...
    NotImplementedError: {'method2', 'method3'}

    This works in both Python 3 and Python 2."""

    def __new__(cls, name, bases, attrs, do_check=True):
        do_check = attrs.get('do_check', do_check)
        if do_check:
            base = bases[0]
            tempattrs = attrs
            while True:
                try:
                    methods = tempattrs['_METHODS']
                    break
                except KeyError:
                    tempattrs = vars(base)
                    base = base.__base__()

            unimplemented = methods - set(attrs)
            if unimplemented:
                raise NotImplementedError(unimplemented)
        else:
            attrs['do_check'] = True
        return type.__new__(cls, name, bases, attrs)


FrontEnd = RequiredMethods('FrontEnd', (), {
    '_METHODS': {"ask_names", "ask_bids", "ask_tricks", "exit", "win"},
    'do_check': False,
})

BackEnd = RequiredMethods('BackEnd', (), {
    '_METHODS': {'add_bids', 'add_tricks', 'get_bids', 'get_deal', 'get_dealer',
                 'get_names', 'get_tricks', 'set_names', 'undo'},
    'do_check': False,
})


class SimpleBackEnd(BackEnd):
    WIN_SCORE = 500
    def __init__(self):
        self.bids = [[]]
        self.names = (None,) * 4
        self.tricks = [[]]
        self.scores = [[(0, 0), (0, 0)]]
        self.deal = 0
        self.winner = False

    def _score(self):
        bids = self.bids[self.deal]
        tricks = self.tricks[self.deal]
        nscores = {NIL: 100, DOUBLE: 200}
        new_scores = []
        for person in (0, 1):
            player = (bids[person], tricks[person])
            partner = (bids[person + 2], tricks[person + 2])
            score = 0
            overtricks = 0
            if any(bid in (NIL, DOUBLE) for bid in (player[0], partner[0])):
                for bid, trick in (player, partner):
                    if bid in (NIL, DOUBLE):
                        score = (sub, add)[trick == 0](score, nscores[bid])
                    elif trick < bid:
                        score -= (bid * 10)
                    else:
                        score += (bid * 10)
                        overtricks += trick - bid
            else:
                bid = max(player[0], partner[0])
                trick = player[1] + partner[1]
                if trick < bid:
                    score -= (bid * 10)
                else:
                    score += (bid * 10)
                    overtricks += trick - bid
            # TODO: Fix here. New scores are in wrong format or something
            old_score, old_overtricks = self.scores[self.deal][person]
            new_score = old_score + score
            new_overtricks = old_overtricks + overtricks
            if new_overtricks >= 10:
                new_overtricks -= 10
                new_score -= 90

            new_scores.append((new_score, new_overtricks))

        winner = max(enumerate(new_scores), key=lambda x: x[1])
        if winner[1][0] >= self.WIN_SCORE:
            self.winner = winner
        self.scores[self.deal] = new_scores

        self.deal += 1
        if self.deal >= len(self.scores):
            self.scores.append(None)
            self.bids.append(None)
            self.tricks.append(None)
        self.bids[self.deal] = [None] * 4
        self.tricks[self.deal] = [None] * 4
        self.scores[self.deal] = self.scores[self.deal - 1]


    def add_bids(self, bids):
        self.bids[self.deal] = tuple(bids)


    def add_tricks(self, tricks):
        self.tricks[self.deal] = tuple(tricks)
        self._score()


    def get_bids(self):
        return self.bids[self.deal]


    def get_deal(self):
        return self.deal


    def get_dealer(self):
        return self.deal % 4


    def get_names(self):
        return self.names


    def get_scores(self):
        return [sum(score) for score in self.scores[self.deal]]


    def get_tricks(self):
        return self.tricks[self.deal]


    def set_names(self, names):
        self.names = tuple(names)


    def undo(self):
        if self.deal == 0:
            raise CannotUndo
        self.deal -= 1



class TerminalFrontEnd(FrontEnd):
    _responses = (
        'Eh, what?', 'No, no, no. Just ... no.', 'Well, I think I can -- no.',
        'Have another buttered roll.', 'And what do you mean by that?',
        "Sorry. I can't permit that.",
    )
    def __init__(self, backend):
        self.backend = backend

    def _print_score(self):
        print("\nScores:\n")
        scores = self.backend.get_scores()
        names = self.backend.get_names()
        print("{0[0]} and {0[2]}: {1}".format(names, scores[0]))
        print("{0[1]} and {0[3]}: {1}".format(names, scores[1]))
        print("\n")


    def _input(self, prompt):
        try:
            try:
                func = raw_input
            except NameError:
                func = input
            reply = func(prompt)
        except KeyboardInterrupt:
            raise Exit()
        if reply in ('bye', 'exit', 'quit'):
            raise Exit
        elif reply.lower() == 'undo':
            raise Undo
        return reply

    def ask_bids(self):
        dealer = self.backend.get_dealer()
        bids = list(self.backend.get_bids())
        names = self.backend.get_names()
        if not bids or bids[-1] is None:
            position = 0
            # This is not the first hand
            if self.backend.deal:
                self._print_score()
        else:
            for _ in range(dealer):
                bids.append(bids.pop(0))
            position = 3
        while True:
            try:
                bid = self._input("{}'s bid: ".format(names[(dealer + position) % 4])).lower()
            except Undo:
                if position == 0:
                    raise
                position -= 1
                continue
            if bid in ('0', 'nil'):
                bid = NIL
            elif bid in ('00', 'double', 'blind', 'double nil', 'blind nil'):
                bid = DOUBLE
            else:
                try:
                    bid = float(bid)
                    modded = bid % 1
                    if modded not in (0, 0.5):
                        print(random.choice(self._responses))
                        continue
                    if modded == 0:
                        bid = int(bid)
                except ValueError:
                    print(random.choice(self._responses))
                    continue

            if not -1 <= bid <= 13:
                print(random.choice(self._responses))
                continue
                            
            if position > 1:
                partner_bid = bids[position - 2]
                if bid in (NIL, DOUBLE):
                    if isinstance(partner_bid, float):
                        print("Your partner doesn't like your bid.")
                        continue
                elif isinstance(bid, float):
                    print("Only the first bid of a partnership can be a half.")
                    continue
                elif bid <= partner_bid:
                    print("Your bid should include your partner's.")
                    continue
            if position < len(bids):
                bids[position] = bid
            elif position == len(bids):
                bids.append(bid)
            else:
                print("Houston, we have a problem.")
                raise Exit
            if position == 3:
                # Bids are asked starting on current dealer, but are stored
                # starting on original dealer
                for _ in range(dealer):
                    bids.insert(0, bids.pop())
                print()
                return bids
            position += 1

    def ask_names(self):
        text = ""
        names = list(self.backend.get_names())
        prompts = ("Dealer's", "Age's", "Dealer's partner's", "Age's partner's")
        if names[-1] is None:
            who = 0
        else:
            who = 3
        while who < 4:
            try:
                prompt = "{} name: ".format(prompts[who])
                name = self._input(prompt)
                if name in names[:who]:
                    print('"{}" is already in use.'.format(name))
                else:
                    names[who] = name
                    who += 1
            except Undo:
                if who != 0:
                    who -= 1
                else:
                    print("Cannot undo")
        print()
        return names

    def ask_tricks(self):
        bids = self.backend.get_bids()
        names = self.backend.get_names()
        tricks = [None, None, None, None]
        total = 0
        position = 0
        while tricks.count(None) > 1:
            nil = False
            partnership_bids = bids[position], bids[(position + 2) % 4]
            if NIL in partnership_bids or DOUBLE in partnership_bids:
                nil = True
                try:
                    taken = self._input("{} tricks: ".format(names[position]))
                except Undo:
                    if position == 0:
                        raise
                    position -= 1
                    continue
            else:
                if position < 2:

                    if tricks.count(None) == 2:
                        tricks[position] = 0
                        continue
                    partnership_names = names[position], names[position + 2]
                    try:
                        taken = self._input("{} and {} tricks: ".format(*partnership_names))
                    except Undo:
                        if position == 0:
                            raise
                        position -= 1
                        continue
                else:
                    taken = 0
            try:
                taken = int(taken)
                if 0 <= taken <= 13:
                    tricks[position] = taken
                    if position < 2 and not nil:
                        tricks[position + 2] = 0
                    position += 1
                else:
                    print(random.choice(self._responses))
            except ValueError:
                print(random.choice(self._responses))

        try:
            missing = tricks.index(None)
            tricks[missing] = 0
            tricks[missing] = 13 - sum(tricks)
        except IndexError:
            pass
        print()
        return tricks

    def exit(self):
        print("See you soon.")
        exit()
        

    def win(self, winner):
        winner_names = self.backend.names[winner[0]], self.backend.names[winner[0] + 2]
        print("{} and {} won with {}!".format(
            self.backend.names[winner[0]], self.backend.names[winner[0] + 2],
            sum(winner[1])
        ))


def main(backend, frontend):
    try:
        frontend.welcome()
    except AttributeError:
        pass
    except Exit:
        frontend.exit()
    try:
        backend.set_names(frontend.ask_names())
    except Exit:
        frontend.exit()
    while not backend.winner:
        try:
            while True:
                backend.add_bids(frontend.ask_bids())
                try:
                    backend.add_tricks(frontend.ask_tricks())
                    break
                except Undo:
                    pass
                except Exit:
                    frontend.exit()
        except Undo:
            try:
                backend.undo()
                frontend.ask_tricks()
            except Exit:
                frontend.exit()
            except Undo:
                backend.undo()
            except CannotUndo:
                try:
                    backend.set_names(frontend.ask_names())
                except Exit:
                    frontend.exit()
        except Exit:
            frontend.exit()
    frontend.win(backend.winner)


if __name__ == '__main__':
    backend = SimpleBackEnd()
    frontend = TerminalFrontEnd(backend)
    main(backend, frontend)
