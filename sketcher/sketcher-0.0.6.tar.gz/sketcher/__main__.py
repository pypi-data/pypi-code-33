"""
This just print an empty sketch to help user starting.
"""
empty = """
#!/usr/bin/env python
from sketcher import sketch, Sketch


@sketch
class Sk(Sketch):
    # you do not need to inherit from sketch but it help auto-completion
    def setup(self):
        pass  # Here come the initialisation

    def loop(self):
        pass  # Here come the per-frame actions
"""
print(empty)
