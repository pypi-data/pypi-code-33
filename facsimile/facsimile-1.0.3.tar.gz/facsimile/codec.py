
import munge.codec.all


def get_codecs():
    return munge.get_codecs()

def list_codecs():
    return [ext[0] for ext in munge.get_codecs().keys()]

def get_codec(typ, codecs=munge.get_codecs()):
    return munge.get_codec(typ, codecs)

def find_datafile(name, search_path, codecs=get_codecs()):
    """
    find all matching data files in search_path
    search_path: path of directories to load from
    codecs: allow to override from list of installed
    returns array of tuples (codec_object, filename)
    """
    return munge.find_datafile(name, search_path, codecs)

def load_datafile(name, search_path, codecs=get_codecs(), **kwargs):
    """
    find datafile and load them from codec
    TODO only does the first one
    kwargs:
    default = if passed will return that on failure instead of throwing
    """
    return munge.load_datafile(name, search_path, codecs, **kwargs)

