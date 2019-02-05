
import logging
import os
import glob


_PATHS = {}
_CACHE = {}
_PIXCACHE = {}
_ICONCACHE = {}


class ResourcesError(Exception):
    pass


class NotFoundError(ResourcesError):
    pass


def add_folder(name, path):
    '''
    Register a folder to the search path.

    The name parameter will be used to retrieve files.

    The path parameter can be a file inside the folder
    to register, or the path of the folder itself.

    If a folder with the same name was previously added, the
    files from the last one overrides the previous one but
    the previous file not available in the last one are
    still accessible. (i.e. the last one overrides and
    extends the previous one.)

    Every file in this folder will be available with:
        import kabaret.app.resources
        kabaret.app.resources.get(folder_name, file_name)
    (See get(), get_pixmap(), ...)

    Typical usage:
        - add resources from a python package:
            import kabaret.app.resources
            kabaret.app.resources.add_folder('icons', __file__)
        - use resources from this package:
            import kabaret.app.resources
            kabaret.app.resources.get('icons', 'maya')

    '''
    global _PATHS, _CACHE

    if not os.path.isdir(path):
        path = os.path.dirname(path)

    if name not in _PATHS:
        _PATHS[name] = []
    _PATHS[name].insert(0, path)

    # Remove cache for this folder name:
    if name in _CACHE:
        _CACHE.pop(name)


def get_folder_names():
    '''
    Returns a list of available folder names.
    '''
    global _PATHS
    return list(_PATHS)


def list_folder(folder_name):
    '''
    Returns a list of resource names available in the given folder_name.
    '''
    global _PATHS

    EXCLUDE_LIST = ('Thumbs.db',)

    folder_name = folder_name.lower()

    ret = set()
    for path in _PATHS[folder_name]:
        ret.update(
            [
                name.split('.', 1)[0]
                for name in os.listdir(path)
                if not name.startswith('_')
                if not name.startswith('.')
                and name not in EXCLUDE_LIST
            ]
        )
    return sorted(ret)


def list_folder_paths(folder_name):
    '''
    Return a list of list of file_name for the given folder_name.
    (overrides come first)
    '''
    global _PATHS

    folder_name = folder_name.lower()

    ret = []
    for path in _PATHS[folder_name]:
        ret.append(sorted(
            [
                name.split('.', 1)[0]
                for name in os.listdir(path)
                if not name.startswith('_')
            ]
        ))
    return ret


def get(folder_name, file_name):
    '''
    Returns the file named file_name and registered
    under the folder folder_name.
    '''
    global _PATHS, _CACHE

    # avoid case sensitive look-up in order to have the same
    # behavior in win$ and Linux:
    folder_name = folder_name.lower()
    file_name = file_name.lower()

    cache_key = (folder_name, file_name)
    if cache_key in _CACHE:
        if _CACHE[cache_key]:
            return _CACHE[cache_key]
        else:
            raise NotFoundError("Resource not found: " + repr(cache_key))

    try:
        path_list = _PATHS[folder_name]
    except KeyError:
        raise ResourcesError(
            "Unknown resource folder " +
            repr(folder_name) + ". (Did you install it first?)"
        )

    files = None
    for path in path_list:
        files = glob.glob(
            os.path.join(
                path,
                file_name + ('.' not in file_name and ".*" or "")
            )
        )
        if files:
            break
    if not files:
        _CACHE[cache_key] = None
        raise NotFoundError("Resource not found: " + repr(cache_key))
    if len(files) > 1:
        logging.getLogger('kabaret.resources').warn(
            "Several resources found for: " + repr(cache_key))

    _CACHE[cache_key] = files[0]
    return files[0]


def get_pixmap(folder_name, pixmap_name):
    '''
    Same as get, but returns a QPixmap
    '''
    global _PIXCACHE

    path = get(folder_name, pixmap_name)
    if path in _PIXCACHE:
        return _PIXCACHE[path]

    from qtpy import QtGui

    ret = QtGui.QPixmap(path)
    _PIXCACHE[path] = ret

    return ret


def get_icon(icon_ref, for_widget=None, disabled_ref=None):
    '''
    If icon ref is an int, for_widget must not be None
    and its current QStyle will be used to return
    the Qt icon pointed by icon_ref.

    If icon_ref is a 2D tuple, it is used to call
    get_pixmap(*icon_ref)

    If icon_ref is a file path, an icon is created from this file.

    if disable_ref is not None, it must be a 2D tuple suitable for
    get_pixmap(*disabled_ref) and will be used as the "disabled"
    state of the icon.

    Warning: using different disabled_ref for the same icon_ref has 
    undefined behavior.

    '''
    if isinstance(icon_ref, int):
        style = for_widget.style()
        return style.standardIcon(icon_ref)

    global _ICONCACHE
    if icon_ref in _ICONCACHE:
        return _ICONCACHE[icon_ref]

    from qtpy import QtGui

    pix = None
    try:
        pix = get_pixmap(*icon_ref)
    except Exception:
        try:
            if os.path.isfile(icon_ref):
                pix = QtGui.QPixmap(icon_ref)
        except TypeError:
            pass

    if pix is None:
        raise NotFoundError('Cannot find icon for %r' % (icon_ref,))

    icon = QtGui.QIcon(pix)

    if disabled_ref is not None:
        pix = get_pixmap(*disabled_ref)
        icon.addPixmap(pix, mode=icon.Disabled)

    _ICONCACHE[icon_ref] = icon
    return icon
