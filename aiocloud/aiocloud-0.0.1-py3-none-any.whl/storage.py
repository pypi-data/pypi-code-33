import functools

from . import helpers


__all__ = ('missing', 'Structure')


missing = type('missing', (), {'__slots__': (), '__bool__': lambda s: False})()


class Structure:

    __slots__ = ('__dict__',)

    def __init__(self, *args, **extra):

        try:

            (data,) = args

        except ValueError:

            pass

        else:

            extra.update(data)

        update_structure(self, extra)

    def __getattr__(self, name, forbidden = '__'):

        if name.startswith(forbidden):

            raise AttributeError(name)

        blueprint = _blueprint(self.__class__)

        available = blueprint.keys()

        if name in available:

            return missing

        raise AttributeError(name)

    def __eq__(self, other):

        family = isinstance(other, self.__class__)

        return family and self.__dict__ == other.__dict__

    def __ne__(self, other):

        return not self.__eq__(other)

    def __hash__(self):

        return super().__hash__()

    def __repr__(self):

        return f'<{self.__class__.__name__}>'


@functools.lru_cache(maxsize = None)
def _structure(name):

    bases = (Structure,)

    namespace = {}

    value = type(name, bases, namespace)

    return value


@functools.lru_cache(maxsize = None)
def _blueprint(structure):

    return _blueprints[structure.__name__]


@functools.lru_cache(maxsize = None)
def _structure_update():

    skip = (missing,)

    def wrapper(value, data):

        blueprint = _blueprint(value.__class__)

        return helpers.update_generic(blueprint, value, data, skip = skip)

    return wrapper


def update_structure(value, data):

    return _structure_update()(value, data)


def _noop_update(value, data):

    return


def _pick_update(value):

    if isinstance(value, type) and issubclass(value, Structure):

        return _structure_update()

    return _noop_update


@functools.lru_cache(maxsize = None)
def _list_update(build):

    update = _pick_update(build)

    return helpers.cached_partial(helpers.update_list, update, build)


def update_list(build, *args, **kwargs):

    return _list_update(build)(*args, **kwargs)


@functools.lru_cache(maxsize = None)
def _dict_update(build, keys):

    update = _pick_update(build)

    identify = helpers.cached_partial(helpers.crawl, keys)

    return helpers.cached_partial(helpers.update_dict, update, build, identify)


def update_dict(build, keys, *args, **kwargs):

    return _dict_update(build, keys)(*args, **kwargs)


@functools.lru_cache(maxsize = None)
def _field(create, update):

    return (create, update)


_string = str


_integer = int


_boolean = bool


_list = list


_dict = dict



_blueprints = {
    'Track': {
        'id': _field(
            _integer,
            None
        ),
        'created_at': _field(
            _string,
            None
        ),
        'user_id': _field(
            _integer,
            None
        ),
        'duration': _field(
            _integer,
            None
        ),
        'commentable': _field(
            _boolean,
            None
        ),
        'state': _field(
            _string,
            None
        ),
        'sharing': _field(
            _string,
            None
        ),
        'tag_list': _field(
            _string,
            None
        ),
        'permalink': _field(
            _string,
            None
        ),
        'description': _field(
            _string,
            None
        ),
        'downloadable': _field(
            _boolean,
            None
        ),
        'genre': _field(
            _string,
            None
        ),
        'release': _field(
            _string,
            None
        ),
        'purchase_url': _field(
            _string,
            None
        ),
        'label_id': _field(
            _integer,
            None
        ),
        'label_name': _field(
            _string,
            None
        ),
        'isrc': _field(
            _string,
            None
        ),
        'video_url': _field(
            _string,
            None
        ),
        'track_type': _field(
            _string,
            None
        ),
        'key_signature': _field(
            _string,
            None
        ),
        'bpm': _field(
            _integer,
            None
        ),
        'title': _field(
            _string,
            None
        ),
        'release_year': _field(
            _integer,
            None
        ),
        'release_day': _field(
            _integer,
            None
        ),
        'release_month': _field(
            _string,
            None
        ),
        'original_format': _field(
            _string,
            None
        ),
        'original_content_size': _field(
            _integer,
            None
        ),
        'licence': _field(
            _string,
            None
        ),
        'uri': _field(
            _string,
            None
        ),
        'permalink_url': _field(
            _string,
            None
        ),
        'artwork_url': _field(
            _string,
            None
        ),
        'waveform_url': _field(
            _string,
            None
        ),
        'user': _field(
            _structure('User'),
            _structure_update()
        ),
        'stream_url': _field(
            _string,
            None
        ),
        'download_url': _field(
            _string,
            None
        ),
        'playback_count': _field(
            _integer,
            None
        ),
        'download_count': _field(
            _integer,
            None
        ),
        'favoritings_count': _field(
            _integer,
            None
        ),
        'comment_count': _field(
            _integer,
            None
        ),
        'attachments_uri': _field(
            _string,
            None
        ),
    },
    'User': {
        'id': _field(
            _integer,
            None
        ),
        'permalink': _field(
            _string,
            None
        ),
        'username': _field(
            _string,
            None
        ),
        'uri': _field(
            _string,
            None
        ),
        'permalink_url': _field(
            _string,
            None
        ),
        'avatar_url': _field(
            _string,
            None
        )
    },
    'Playlist': {
        'id': _field(
            _integer,
            None
        ),
        'created_at': _field(
            _string,
            None
        ),
        'user_id': _field(
            _integer,
            None
        ),
        'user': _field(
            _structure('User'),
            _structure_update()
        ),
        'tracks': _field(
            _list,
            _list_update(
                _structure('Track')
            )
        ),
        'title': _field(
            _string,
            None
        ),
        'permalink': _field(
            _string,
            None
        ),
        'permalink_url': _field(
            _string,
            None
        ),
        'uri': _field(
            _string,
            None
        ),
        'sharing': _field(
            _string,
            None
        ),
        'embeddable_by': _field(
            _string,
            None
        ),
        'purchase_url': _field(
            _string,
            None
        ),
        'artwork_url': _field(
            _string,
            None
        ),
        'description': _field(
            _string,
            None
        ),
        'label': _field(
            _structure('User'),
            _structure_update()
        ),
        'duration': _field(
            _integer,
            None
        ),
        'genre': _field(
            _string,
            None
        ),
        'tag_list': _field(
            _string,
            None
        ),
        'label_id': _field(
            _integer,
            None
        ),
        'label_name': _field(
            _string,
            None
        ),
        'release': _field(
            _string,
            None
        ),
        'release_day': _field(
            _integer,
            None
        ),
        'release_month': _field(
            _integer,
            None
        ),
        'release_year': _field(
            _integer,
            None
        ),
        'streamable': _field(
            _boolean,
            None
        ),
        'downloable': _field(
            _boolean,
            None
        ),
        'ean': _field(
            _string,
            None
        ),
        'playlist_type': _field(
            _string,
            None
        )
    }
}


@functools.lru_cache(maxsize = None)
def __getattr__(name):

    available = _blueprints.keys()

    if not name in available:

        raise AttributeError(name)

    return _structure(name)


__all__ = (*__all__, *_blueprints.keys())
