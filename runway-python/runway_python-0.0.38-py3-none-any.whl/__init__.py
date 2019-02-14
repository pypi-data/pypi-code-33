# from .model import RunwayModel, __version__

import sys

def setup(options):
    def decorator(fn):
        module = sys.modules[fn.__module__]
        setattr(module, 'runway_setup', fn)
        setattr(module, 'runway_setup_options', options)
        return fn
    return decorator

def command(name, inputs, outputs):
    def decorator(fn):
        module = sys.modules[fn.__module__]
        setattr(module, 'runway_command_count', getattr(module, 'runway_command_count', -1) + 1)
        setattr(module, 'runway_command_%d' % getattr(module, 'runway_command_count'), fn)
        setattr(module, 'runway_command_%d_options' % getattr(module, 'runway_command_count'), dict(name=name, inputs=inputs, outputs=outputs))
        return fn
    return decorator
