import functools

def emit_log_event(f):
    functools.wraps(f)
    def wrapped(self, tag, *f_args, **f_kwargs):
        f(self, tag, *f_args, **f_kwargs)
        self.emit_event(tag, *f_args, **f_kwargs)
    return wrapped

def namespaced_logger(f):
    functools.wraps(f)
    def wrapped(self, tag, *f_args, **f_kwargs):
        if self.current_context:
            tag = f"{self.current_context}/{tag}"

        f(self, tag, *f_args, **f_kwargs)
    return wrapped