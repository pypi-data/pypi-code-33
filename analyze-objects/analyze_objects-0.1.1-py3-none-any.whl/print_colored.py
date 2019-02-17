import colorama


def init_print_colored():
    """Initializes colored printing."""
    colorama.init()


def _print_colored(color, *args, **kwargs):
    """Calls print() with the given args and uses the given text color."""
    print(colorama.Style.BRIGHT + color, end="")
    print(*args, **kwargs)
    print(colorama.Style.RESET_ALL, end="")


def print_green(*args, **kwargs):
    """Calls print() with the given args and uses a green text color."""
    _print_colored(colorama.Fore.GREEN, *args, **kwargs)


def print_red(*args, **kwargs):
    """Calls print() with the given args and uses a red text color."""
    _print_colored(colorama.Fore.RED, *args, **kwargs)


def print_white(*args, **kwargs):
    """Calls print() with the given args and uses a white text color."""
    _print_colored(colorama.Fore.WHITE, *args, **kwargs)


def print_yellow(*args, **kwargs):
    """Calls print() with the given args and uses a yellow text color."""
    _print_colored(colorama.Fore.YELLOW, *args, **kwargs)
