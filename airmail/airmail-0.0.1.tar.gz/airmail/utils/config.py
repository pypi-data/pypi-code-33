from functools import reduce

def build_config(transforms, config):
    """Reduces a dictionary through functions to modify the dictionary"""
    return reduce(lambda c, fn: fn(c), transforms, config)
