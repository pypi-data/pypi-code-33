
from . import abstract


__all__ = ('sub', 'trail', 'prefix', 'parse', 'analyse', 'context')


def sub(store, *names, cls = None):

    def decorator(invoke):

        value = (cls or dict)()

        state = (invoke, value)

        for name in names:

            store[name] = state

        return value

    return decorator


def trail(store, *names):

    return abstract.trail(store, names)


def prefix(values, content):

    for value in values:

        if content.startswith(value):

            break

    else:

        raise ValueError()

    content = content[len(value):]

    return value, content


lower = '.'


middle = ' '


upper = ' '


def parse(content, lower = lower, middle = middle):

    return abstract.parse(content, lower, middle)


def analyse(store, content, parse = parse):

    names, argument = parse(content)

    invoke = trail(store, *names) if names else None

    return names, argument, invoke


def context(store, starts, content, prefix = prefix, analyse = analyse):

    start, content = prefix(starts, content)

    names, argument, invoke = analyse(store, content)

    return start, names, argument, invoke


class Store(dict):

    __slots__ = ()

    def sub(self, *names, use = sub):

        return use(self, *names, cls = self.__class__)

    def trail(self, *names, use = trail):

        return use(self, *names)

    def analyse(self, content, use = analyse):

        return use(self, content)

    def context(self, starts, value, use = context):

        return use(self, starts, value)
