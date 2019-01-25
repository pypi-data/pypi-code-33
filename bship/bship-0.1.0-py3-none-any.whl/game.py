from battleship.engine import Engine


def run():
    """Runs the Engine methods in the right order.
    """
    game = Engine()

    game.start()
    game.set()
    game.play()
    if game.end():
        return run()
    print("good game!")


def game_type():
    """User can choose playing against computer or another user.
    """
    pass


if __name__ == "__main__":
    run()
