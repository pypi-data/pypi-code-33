import datetime
import os.path


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
