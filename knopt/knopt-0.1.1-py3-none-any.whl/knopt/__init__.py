from argparse import ArgumentParser
import inspect

def arg(*names, **kwargs):
    base = kwargs.get('type', str)
    return type(base.__name__, (base,),
                {**kwargs, 'names': names})

def main(f=None, **kwargs):
    def decorator(f):
        run_method = None
        if 'run' in kwargs:
            run_method = kwargs['run']
            del kwargs['run']
        if run_method is None:
            return run(f)

        @staticmethod
        def do_now():
            run(f)
            return None
        setattr(f, run_method, do_now)
        return f

    def run(f):
        if f.__doc__ is not None:
            kwargs['description'] = f.__doc__
        if 'default' in kwargs:
            default_method = kwargs['default']
            del kwargs['default']
        else:
            default_method = None
        parser = ArgumentParser(**kwargs)
        if isinstance(f, type):
            init = getattr(f, '__init__')
            _setup_parser(parser, init, method=True)
            subs = parser.add_subparsers(title=init.__doc__)

            for method in dir(f):
                if method.startswith('_'): continue

                sub = subs.add_parser(method)
                fun = getattr(f, method)
                _setup_parser(sub, fun, method=True)
                sub.set_defaults(_run=fun)

            args = parser.parse_args()
            obj = f(*_build_args(init, args, method=True))

            if '_run' not in args:
                # no subparser selected, just run default
                if default_method is not None:
                    fun = getattr(f, default_method)
                    sub = subs.choices[fun.__name__]
                    _setup_parser(sub, init, method=True)
                    args = sub.parse_args()
                else:
                    raise Exception("no command selected")
            _call_with_args(args._run, args, self=obj)
        else:
            _setup_parser(parser, f)
            args = parser.parse_args()
            _call_with_args(f, args)
        return f
    if f is None: return decorator
    return decorator(f)

def _arg_name(a):
    if len(a) > 1:
        return '--' + a
    else:
        return '-' + a

def _setup_parser(parser, f, method=False):
    if f.__doc__ is not None:
        parser.description = f.__doc__
    spec = inspect.signature(f).parameters
    args = list(spec.keys())
    if method: args = args[1:]
    for a in args:
        params = [a]
        kwparams = {}
        ann = spec[a].annotation
        positional = False
        if ann != inspect._empty:
            kwparams['type'] = ann
            alts = getattr(ann, 'names', [])
            for alt in alts:
                params.append(alt)
            if hasattr(ann, 'help'):
                kwparams['help'] = getattr(ann, 'help')
            if hasattr(ann, 'action'):
                kwparams['action'] = getattr(ann, 'action')
            positional = getattr(ann, 'positional', False)
        default = spec[a].default
        if not positional:
            params = map(_arg_name, params)
            if default == inspect._empty:
                kwparams['required'] = True
            else:
                kwparams['default'] = default

        parser.add_argument(*params, **kwparams)

def _build_args(f, args, method=False):
    spec = inspect.getfullargspec(f)
    f_args = spec.args
    if method:
        f_args = f_args[1:]
    for a in f_args:
        yield getattr(args, a)

def _call_with_args(f, args, self=None):
    if self is None:
        return f(*_build_args(f, args))
    else:
        return f(self, *_build_args(f, args, method=True))
