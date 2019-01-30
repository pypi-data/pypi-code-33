""" useful code for instrumenting asynchronous Python programs
# (c) 2016 SolarWinds, LLC.
"""
from appoptics_apm import util


class AppOpticsApmContextManager(object):
    """ A context manager (for the "with" statement) that sets and
        clears the context when entered, storing the metadata in an
        object passed by the constructor.  E.g.:

        with AppOpticsApmContextManager(self.request):
            do_something()

        Here, any code called from do_something() will have its appoptics_apm
        context set from (and stored to, after finishing) the
        self.request object.
    """

    def __init__(self, ctxobj=None):
        """ stores appoptics_apm metadata as attribute of object 'ctxobj' """
        self.obj = ctxobj

    def __enter__(self):
        ctx = getattr(self.obj, '_appoptics_apm_ctx', None)
        if ctx and ctx.is_valid():
            ctx.set_as_default()
        elif util.Context.get_default().is_valid():
            util.Context.clear_default()

    def __exit__(self, type, value, tb):
        default_ctx = util.Context.get_default()
        if default_ctx.is_valid():
            ctx = default_ctx.copy()
            setattr(self.obj, '_appoptics_apm_ctx', ctx)
            util.Context.clear_default()
