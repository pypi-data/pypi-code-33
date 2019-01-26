# -*- coding: utf-8 -*-

import os
import json
import gzip

import six
from six.moves import cPickle as pickle
from six import StringIO

try:
    import numpy as np
except ImportError:
    np = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import cv2
    cv2_IMREAD_UNCHANGED = cv2.IMREAD_UNCHANGED
except ImportError:
    cv2 = None
    cv2_IMREAD_UNCHANGED = -1

import humanize

import path


class Path(path.Path):

    def purebasename(self):
        """ Combines basename and stripext.
        Turns out to be alias for namebase property.
        """
        return self.namebase


    def write_gzip_bytes(self, bytes, compresslevel=5):
        """ Open this file, gzip and write the given bytes.

        Default behavior is to overwrite any existing file.
        Call ``p.write_bytes(bytes, append=True)`` to append instead.
        """
        sio = StringIO()
        with gzip.GzipFile(None, 'w', compresslevel, sio) as gz:
            gz.write(bytes)
        with self.open('wb') as f:
            f.write(sio.getvalue())


    def read_gzip_bytes(self):
        """ Open this file, read all bytes, return them as a string. """
        with gzip.open(self, 'rb') as f:
            return f.read()


    def read_json(self, *args, **kwargs):
        """ Write contents of file as JSON.
        """
        with self.open('rb') as f:
            return json.load(f, *args, **kwargs)


    def write_json(self, obj, mode='wb', **kwargs):
        """ Write contents of file as JSON.
        """
        with self.open(mode) as f:
            return json.dump(obj, f, **kwargs)


    def read_pickle(self):
        with self.open('rb') as f:
            return pickle.load(f)


    def write_pickle(self, obj, mode='wb', **kwargs):
        """ Write contents of file as pickle.
        """
        with self.open(mode) as f:
            return pickle.dump(obj, f, **kwargs)


    def read_numpy(self, **kwargs):
        if np is None:
            raise NotImplementedError('numpy not available')
        with self.open('rb') as f:
            return np.load(f, **kwargs)


    def write_npz_compressed(self, *args, **kwargs):
        if np is None:
            raise NotImplementedError('numpy not available')
        np.savez_compressed(str(self), *args, **kwargs)


    def write_npz(self, *args, **kwargs):
        if np is None:
            raise NotImplementedError('numpy not available')
        np.savez(str(self), *args, **kwargs)


    def read_pil(self, **kwargs):
        if Image is None:
            raise NotImplementedError('PIL.Image is not available')
        return Image.open(self, **kwargs)


    def write_pil(self, img, **kwargs):
        if Image is None:
            raise NotImplementedError('PIL.Image is not available')
        if not isinstance(img, Image.Image):
            raise ValueError('img is not a PIL Image')
        img.save(str(self), **kwargs)


    def read_cv2(self, to_rgb=False, flags=cv2_IMREAD_UNCHANGED):
        if cv2 is None:
            raise NotImplementedError('cv2 is not available')
        img = cv2.imread(self, flags)
        if to_rgb and (img is not None) and img.ndim==3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img


    def write_cv2(self, img, params=[]):
        if cv2 is None:
            raise NotImplementedError('cv2 is not available')
        return cv.imwrite(str(self), img, params)


    def read_pandas_csv(self, **kwargs):
        if pd is None:
            raise NotImplementedError('pandas is not available')

        with self.open('rb') as f:
            return pd.read_csv(f, **kwargs)


    def getnaturalsize(self):
        return humanize.naturalsize(self.getsize())


    @property
    def naturalsize(self):
        """ String with humanized file size. """
        return self.getnaturalsize()


    def sorted_files(self, pattern=None):
        """ List of files in this directory, sorted. """
        return sorted(self.files(pattern))


    def sorted_dirs(self, pattern=None):
        """ List of dirs in this directory, sorted. """
        return sorted(self.dirs(pattern))


    @classmethod
    def gethome(cls):
        """ Return home dir

        """
        if 'HOME' in os.environ:
            userhome = os.environ['HOME']
        elif 'USERPROFILE' in os.environ:
            userhome = os.environ['USERPROFILE']
        else:
            raise RuntimeError("Can't determine home directory")
        return cls(userhome)
