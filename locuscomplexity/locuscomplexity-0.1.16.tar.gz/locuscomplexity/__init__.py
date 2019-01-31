import os

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_data(path):
    return os.path.join(_ROOT, path)

import locuscomplexity.fitness, locuscomplexity.complexity, locuscomplexity.color_code
__all__ = ["color_code", "fitness", "complexity"]

