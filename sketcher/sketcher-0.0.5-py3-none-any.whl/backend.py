supported_backends = [
    # "pyglet",  # not ready yet
    "tkinter",
]


class NoBackend(BaseException):
    def __init__(self):
        super().__init__(
            "There is no supported graphical backend installed.\n" +
            "Try to install one of those:\n" +
            "\n".join("- " + back for back in supported_backends)
        )


try:
    import pyglet
    have_pyglet = True
except ImportError:
    have_pyglet = False 


try:
    import tkinter
    have_tk = True
except ImportError:
    have_tk = False
have_pyglet = False  # in progress

if have_pyglet:
    from .backend_pyglet import Backend
elif have_tk:
    from .backend_tk import Backend
else:
    raise NoBackend()
