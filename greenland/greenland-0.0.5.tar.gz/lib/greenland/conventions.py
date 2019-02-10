

def longstr(obj, *pargs, **kwargs):
    try:
        return obj.__longstr__(*pargs, **kwargs)
    except AttributeError:
        return str(obj)


class UserError(Exception):
    pass
