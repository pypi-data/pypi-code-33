import os
import re
import errno
import numpy as np


_SUFFIX_PATTERNS = [
    r"_\d+(bit|bits)_\d+(x\d+)+",
    r"_\d+(x\d+)+_\d+(bit|bits)",
    r"_\d+(x\d+)+",
    r"_\d+(bit|bits)"
]
_NBIT_PATTERN = r"(^\d+(?=bit|bits))?(\w*(?=_)_)?(\d+(?=bit|bits))?"
_SHAPE_PATTERN = r"(\w+(?=\d+x))?(?P<SHAPE>((?<=_)\d+(x\d+)+)|^(\d+(x\d+)+))\w*"
_PREFIX_SUFFIX_PATTERN = r"(?P<PREFIX>{})_(?P<SUFFIX>\w+(?=\.\w+)|\w+)?".format("|".join(r"[0-9a-zA-Z_\-]+(?=%s)" % pattern for pattern in _SUFFIX_PATTERNS))


_NBIT_TO_DTYPE = {
    '8': np.uint8,
    '16': np.float16,
    '32': np.float32,
    "64": np.float64
}
_DEFAULT_DTYPE = np.uint8


def _safe_cast(V, T, default=None):
    try:
        return T(V)
    except (ValueError, TypeError):
        return default


def _meta_information_imagej_format(dtype, shape):
    return "{}bit_".format(dtype.itemsize * 8) + "x".join([str(s) for s in shape[::-1]])


def parse_filename(filename):
    """Parse filename to get prefix and such meta information as the shape and number of bits per value.
    
    Arguments:
        filename (str) -- filename or file path
    
    Raises:
        RuntimeError -- if filename cannot be parsed for some reason
    
    Returns:
        (tuple) -- (prefix, shape, dtype)
    """
    filename = os.path.basename(filename)
    dtype, shape = None, None

    # Split the filename on PREFIX and SUFFIX
    r = re.match(_PREFIX_SUFFIX_PATTERN, filename)
    prefix, suffix = r.group('PREFIX'), r.group('SUFFIX')
    
    # Parse SUFFIX if presented
    if suffix:
        # Parse the number of bits if given
        r = re.match(_NBIT_PATTERN, suffix)
        if r:
            groups = r.groups()
            if groups[0] is not None and groups[2] is not None:
                raise RuntimeError("Two specifications of bits was found.")
        
            nbit = groups[2] if groups[0] is None else groups[0]

        dtype = _NBIT_TO_DTYPE[nbit] if nbit in _NBIT_TO_DTYPE else _DEFAULT_DTYPE
        
        # Parse the SHAPE if given
        r = re.match(_SHAPE_PATTERN, suffix)
        shape = r.group('SHAPE') if r else None
        if shape is None:
            # Check that the PREFIX is not the SHAPE
            r = re.match(_SHAPE_PATTERN, prefix)
            _shape = r.group('SHAPE') if r else None
            if _shape == prefix:
                shape = _shape
                prefix = None
        
        if shape:
            shape = tuple(_safe_cast(d, int) for d in shape.split('x'))[::-1]

    return (prefix, shape, dtype)


def read_infofile(filepath):
    """Read the '.info' file which is available sometimes for data we have.
    
    Arguments:
        filepath (str) -- path to the .info file
    
    Returns:
        (tuple) -- (shape, dtype)
    """
    assert filepath is not None, "filepath shoud not be None"
    dtypes = {
        "UINT8": np.uint8,
        "FLOAT32": np.float32,
        "FLOAT64": np.float64,
        "DOUBLE": np.float64,
    }

    with open(filepath, 'r') as f:
        kv_tuples = list(zip(*zip(*[re.sub('[\n]', '', row).split('=') for row in f.readlines()])))
        info = {k.upper(): v for k, v in kv_tuples}
        shape = tuple(_safe_cast(info[k], int) for k in ['NUM_Z', 'NUM_Y', 'NUM_X'])
        dtype = dtypes[info['FORMAT']]

    return (shape, dtype)


def imread(filepath, infofilepath=None):
    """Read the image from the file specified by filepath.
    
    Arguments:
        filepath (str) -- path to the image file
    
    Keyword Arguments:
        infofilepath (str) -- path to the '.info' file (optional)
    
    Raises:
        OSError -- if the file was not found.
    
    Returns:
        (numpy.ndarray) -- image
    """
    assert filepath is not None, "filepath cannot be None"

    if not os.path.exists(filepath):
        raise OSError(errno.ENOENT, "File %r does not exist" % filepath)

    if os.path.exists(filepath) and not os.path.isfile(filepath):
        raise OSError(errno.EISDIR, "filepath should be a path to a file")

    _, shape, dtype = parse_filename(filepath)
    if (shape is None or dtype is None) and (infofilepath is not None):
        if not os.path.exists(infofilepath):
            raise OSError(errno.ENOENT, "File %r does not exist" % infofilepath)
        shape, dtype = read_infofile(infofilepath)

    return np.fromfile(filepath, dtype=dtype, count=-1).reshape(shape)


def imsave(dirpath, prefix, data):
    """Write image data to the RAW file.
    
    Arguments:
        dirpath (str) -- path to the directory to save the image
        prefix (str) -- prefix for the filename
        data (array_like) -- image data
    
    Raises:
        OSError -- if dirpath does not point to the directory
    
    Returns:
        (str) -- filepath to the image
    """

    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    if not os.path.isdir(dirpath):
        raise OSError(errno.ENOTDIR, "dirpath should be a path to a directory")

    suffix = _meta_information_imagej_format(data.dtype, data.shape)
    filename = "{}_{}.raw".format(prefix, suffix)
    filepath = os.path.join(dirpath, filename)
    data = np.array(data)
    data.tofile(filepath)
    return filepath