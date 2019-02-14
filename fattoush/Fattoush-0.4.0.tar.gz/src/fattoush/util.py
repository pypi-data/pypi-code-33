import datetime
import functools
import os.path
import time

import future.utils

LOGFILE_NAME_TEMPLATE = (
    "{datetime:%Y%m%d_%H%M%S.%f}{parent_name} - {sentence}.{ext}"
)


def truncate(long_string, max_length, link_with='...'):
    if len(long_string) <= max_length:
        return long_string

    text_length = max_length - len(link_with)
    end_size = int(text_length / 4)
    start_size = text_length - end_size

    return "{start}{link}{end}".format(
        start=long_string[:start_size],
        end=long_string[-end_size:],
        link=link_with,
    )


def filename_for_step(
    step,
    ext,
    template=LOGFILE_NAME_TEMPLATE,
    max_characters=200,
    **extra_format_string_kwargs
):
    """
    On some platforms filename length is limited to 200 characters. In
    order to work with this let's trim down a few parts to try and keep
    the file names useful.
    """
    parent = step.parent
    parent_name = getattr(parent, 'name', None)
    now = datetime.datetime.now()

    mandatory_characters = len(template.format(
        datetime=now,
        parent_name='',
        sentence='',
        ext=ext,
        **extra_format_string_kwargs
    ))

    if parent_name is None:  # Must be a background
        parent_name = parent.feature.name

    characters_left = max_characters - mandatory_characters

    parent_name = truncate(parent_name, characters_left / 2)

    characters_left -= len(parent_name)

    sentence = truncate(step.sentence, characters_left)

    return template.format(
        sentence=sentence,
        parent_name=parent_name,
        datetime=now,
        ext=ext,
        **extra_format_string_kwargs
    )


def filename_in_created_dir(dir_name, step, ext, **kwargs):
    dir_name = os.path.abspath(dir_name)

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    return os.path.join(dir_name, filename_for_step(step, ext=ext, **kwargs))


def try_map(fn, args_iterable):
    ex = None
    failures = []

    for args in args_iterable:
        try:
            yield fn(args)
        except Exception as ex:
            print(ex)

            failures.append((ex, args))

    if ex is not None:
        msg = '\n\t'.join(
            ['Failed to map {} against all args:'.format(fn)] +
            [
                '{}({}) failed with {}'.format(fn, args, ex)
                for ex, args in failures
            ]
        )

        _runtime_from(msg, ex)


def _runtime_from(msg, cause):
    return future.utils.raise_from(RuntimeError(msg), cause)


def retry(times=1, wait=0, catch=RuntimeError):

    def decorator(fn):
        @functools.wraps(fn)
        def _inner(*args, **kwargs):
            ex = None

            for _ in xrange(times):
                try:
                    return fn(*args, **kwargs)
                except catch as ex:
                    time.sleep(wait)

            if ex is not None:
                msg = '{}(*{}. **{}) failed {} times'.format(
                    fn, args, kwargs, times
                )
                _runtime_from(msg, ex)

        return _inner

    return decorator


def _attrs(obj, include_private=False):
    """ Iterate over a namespace as name-value pairs """
    for name in dir(obj):
        if name.startswith('_') and not include_private:
            continue

        yield name, getattr(obj, name)

def flatmap(obj, to_cls=None):
    """
    Flatmap a decorated function over a namespace

    In the absence of `to_cls` this creates a generator. With
    `to_cls` that generator will be exhausted into an instance
    of that class.

    This is useful for creating say a dictionary within a
    class' namespace without polluting it with extra mess
    """
    def iter_(fn):
        for name, value in _attrs(obj):
            for item in fn(name, value):
                yield item

    if to_cls is None:
        return iter_

    def do(fn):
        return to_cls(iter_(fn))

    return do
