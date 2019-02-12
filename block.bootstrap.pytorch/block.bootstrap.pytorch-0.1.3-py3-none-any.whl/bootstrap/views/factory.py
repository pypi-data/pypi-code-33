import importlib
from ..lib.options import Options
from ..lib.logger import Logger
from .plotly import Plotly

def factory(engine=None):
    Logger()('Creating view...')

    view = None

    if 'view' in Options():
        if 'import' in Options()['view']:
            module = importlib.import_module(Options()['view']['import'])
            view = module.factory()
        else:
            view_name = Options().get('view.name', 'plotly')
            if view_name == 'tensorboard':
                # Lazy import for unused libraries
                from .tensorboard import Tensorboard
                view = Tensorboard(Options())
            elif view_name != 'plotly':
                Logger.log_message("Unknown view name '{}'. Defaulting to plotly.".format(view_name), Logger.WARNING)
                view = Plotly(Options()) # backward compatibility

    return view
