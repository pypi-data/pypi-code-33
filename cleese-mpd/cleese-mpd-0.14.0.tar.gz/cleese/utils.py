import sys

from os.path import basename

from ampdup import Song

from wrapt import decorator


@decorator
async def printer(f, _, args, kwargs):
    '''Print the return of a function f.'''
    print(await f(*args, **kwargs))


@decorator
async def line_list_printer(f, _, args, kwargs):
    '''Print the return of a function f as a list of lines.'''
    for line in await f(*args, **kwargs):
        print(line)


@decorator
async def enum_printer(f, _, args, kwargs):
    '''Print the return of a function f.'''
    print((await f(*args, **kwargs)).value)


def fmtsong(song: Song) -> str:
    '''Format song artist, album and title data.'''
    return '/'.join((song.artist, song.album, song.title))


def fmt_minutes(seconds):
    '''Format seconds as minutes and seconds.

    Args:
        seconds (int): The number of seconds.

    Returns:
        str: The value formatted as `mm:ss`.
    '''
    m, s = divmod(seconds, 60)
    return f'{m}:{s:02}'


def fail(message, name=basename(sys.argv[0]), retval=-1):
    '''Exit with non-zero code printing a message to stderr.'''
    print(f'{name}: {message}', file=sys.stderr)
    sys.exit(retval)
