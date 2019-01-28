import json
import os
import uuid

from datetime import datetime, timedelta
from functools import partial

from drongo import HttpResponseHeaders


class FileNotFoundException(Exception):
    pass


FileNotFoundError = FileNotFoundException()


class Filesystem(object):
    def __init__(self, app, **config):
        self.app = app

        self.path = config.get('filesystem_path')

        self.age = config.get('age', 300)
        self.base_url = config.get('base_url', '/media')
        self.max_depth = config.get('max_depth', 6)

    def init(self):
        self.init_urls()

    def _normalize_container(self, value):
        # TODO: Fix up special characters to safe ones
        value.replace('..', '__')  # Protect against directory attacks
        while value.startswith('/'):
            value = value[1:]

        return value

    def put(self, container, fd, metadata):
        container = self._normalize_container(container)

        folder = os.path.join(self.path, container)
        if not os.path.exists(folder):
            os.makedirs(folder)

        while True:
            key = uuid.uuid4().hex
            fpath = os.path.join(folder, key)
            if not os.path.exists(fpath):
                break

        size = 0
        with open(fpath, 'wb') as wfd:
            for chunk in iter(partial(fd.read, 102400), b''):
                wfd.write(chunk)
                size += len(chunk)

        metadata['size'] = size
        metadata['physical_path'] = fpath

        with open(fpath + '.meta', 'w') as mfd:
            json.dump(metadata, mfd)

        return key

    def get(self, container, key):
        container = self._normalize_container(container)
        folder = os.path.join(self.path, container)
        fpath = os.path.join(folder, key)

        if os.path.exists(fpath):
            with open(fpath + '.meta') as mfd:
                return open(fpath, 'rb'), json.load(mfd)

        raise FileNotFoundError

    def get_url(self, container, key):
        return '{base_url}/{container}/{key}'.format(
            base_url=self.base_url,
            container=container,
            key=key
        )

    def delete(self, container, key):
        container = self._normalize_container(container)
        folder = os.path.join(self.path, container)
        fpath = os.path.join(folder, key)

        if os.path.exists(fpath):
            os.unlink(fpath)
            os.unlink(fpath + '.meta')
            return

        raise FileNotFoundError

    def list(self, container):
        raise NotImplementedError

    def init_urls(self):
        parts = ['', '{a}', '{b}', '{c}', '{d}', '{e}', '{f}']
        for i in range(2, self.max_depth + 2):
            self.app.add_url(
                pattern=self.base_url + '/'.join(parts[:i]),
                call=self._serve_media)

    def _chunks(self, fd):
        for chunk in iter(partial(fd.read, 102400), b''):
            yield chunk
        fd.close()

    # helper functions
    def serve(self, ctx, container, key):
        fd, meta = self.get(container, key)
        ctype = meta.get('mimetype')
        size = meta.get('size')
        expires = datetime.utcnow() + timedelta(seconds=(self.age))
        expires = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')

        ctx.response.set_header(HttpResponseHeaders.CACHE_CONTROL,
                                'max-age=%d' % self.age)
        ctx.response.set_header(HttpResponseHeaders.EXPIRES, expires)
        ctx.response.set_header(HttpResponseHeaders.CONTENT_TYPE, ctype)
        ctx.response.set_content(self._chunks(fd), size)

    def _serve_media(self, ctx,
                     a=None, b=None, c=None, d=None, e=None, f=None):
        parts = [a, b, c, d, e, f]
        while None in parts:
            parts.remove(None)

        container = '/'.join(parts[:-1])
        key = parts[-1]

        self.serve(ctx, container, key)
