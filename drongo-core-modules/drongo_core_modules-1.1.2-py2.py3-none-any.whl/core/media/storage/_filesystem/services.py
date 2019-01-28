from datetime import datetime, timedelta
from functools import partial

import os
import uuid

from drongo import HttpResponseHeaders

import jwt
from PIL import Image

from ... import models


class MediaServiceBase(object):
    FS_DIR = None
    AGE = 3600 * 12

    ENABLE_TINYPNG = False
    TINYPNG_KEY = None

    TOKEN_SECRET = 'DRONGOMEDIASUPERSECRET!@#123$%^456'

    @classmethod
    def init(cls, config):
        cls.FS_DIR = config.get('fs_dir')
        if not os.path.exists(cls.FS_DIR):
            os.makedirs(cls.FS_DIR)

        cls.ENABLE_TINYPNG = config.get('enable_tinypng')
        cls.TINYPNG_KEY = config.get('tinypng_key')

        if cls.ENABLE_TINYPNG:
            import tinify
            tinify.key = cls.TINYPNG_KEY


class ContainerCreateService(MediaServiceBase):
    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def call(self):
        models.Container.create(
            name=self.name,
            description=self.description
        )


class ContainerGetService(MediaServiceBase):
    def __init__(self, name):
        self.name = name

    def call(self):
        container = models.Container.objects.find_one(name=self.name)
        if container is None:
            container = models.Container.create(
                name=self.name)
        return container


class ContainerUpdateService(MediaServiceBase):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def call(self):
        container = ContainerGetService(self.name).call()
        container.description = self.description
        container.save()


class ContainerDeleteService(MediaServiceBase):
    def __init__(self, name):
        self.name = name

    def call(self):
        container = ContainerGetService(self.name).call()
        container.delete()
        # TODO: Delete all the media as well here!


class ContainerListService(MediaServiceBase):
    def call(self):
        return models.Container.objects.find()


class MediaListService(MediaServiceBase):
    def __init__(self, container):
        self.container = container

    def call(self):
        return models.MediaFile.objects.find(container=self.container)


class MediaServeService(MediaServiceBase):
    def __init__(self, container, key, query, response, token=None):
        self.container = container
        self.key = key
        self.query = query
        self.response = response
        self.token = token

    def _chunks(self, fd):
        for chunk in iter(partial(fd.read, 102400), b''):
            yield chunk
        fd.close()

    def bake_query(self):
        baked_query = ''
        if 'width' in self.query:
            baked_query += 'width' + self.query['width'][0]
        if 'height' in self.query:
            baked_query += 'height' + self.query['height'][0]
        if 'quality' in self.query:
            baked_query += 'quality' + self.query['quality'][0]

        self.baked_query = baked_query

    def create_image(self, base_path, new_path):
        img = Image.open(base_path)
        w, h = img.size

        nw = None

        if 'width' in self.query:
            nw = int(self.query['width'][0])
            nh = int(nw / w * h)

        if 'height' in self.query:
            nh = int(self.query['height'][0])
            nw = int(nh / h * w)
        imformat = img.format

        if nw is not None:
            img = img.resize((nw, nh), Image.ANTIALIAS)

        img.save(new_path, imformat)

        if self.ENABLE_TINYPNG:
            import tinify
            source = tinify.from_file(new_path)
            source.to_file(new_path)

    def serve(self, media_file):
        if media_file.info.get('protected'):
            if self.token is None:
                self.response.set_content('Access denied!')
                return

            try:
                token = jwt.decode(
                    self.token, self.TOKEN_SECRET,
                    algorithms=['HS256'])
            except Exception:
                self.response.set_content('Access denied!')
                return

            if not token:
                self.response.set_content('Access denied!')
                return

            if token['container'] != self.container \
                    or token['key'] != self.key:
                self.response.set_content('Access denied!')
                return

        self.bake_query()

        fpath_base = media_file.info.get('physical_filepath')
        fpath = fpath_base + self.baked_query
        if self.baked_query and not os.path.exists(fpath):
            self.create_image(fpath_base, fpath)

        fsize = os.stat(fpath).st_size
        fd = open(fpath, 'rb')
        expires = datetime.utcnow() + timedelta(seconds=(self.AGE))
        expires = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')

        self.response.set_header(HttpResponseHeaders.CACHE_CONTROL,
                                 'max-age=%d' % self.AGE)
        self.response.set_header(HttpResponseHeaders.EXPIRES, expires)

        self.response.set_header(
            HttpResponseHeaders.CONTENT_TYPE, media_file.mimetype)
        self.response.set_content(self._chunks(fd), fsize)

    def call(self):
        media_file = models.MediaFile.objects.find_one(
            container=self.container, key=self.key)

        if media_file is not None:
            self.serve(media_file)


class MediaIssueTokenService(MediaServiceBase):
    def __init__(self, container, key):
        self.container = container
        self.key = key

    def call(self):
        token = jwt.encode({
            'container': self.container,
            'key': self.key,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow()
            + timedelta(seconds=300)
        }, self.TOKEN_SECRET, algorithm='HS256')
        return token.decode('ascii')


class SaveMediaService(MediaServiceBase):
    def __init__(self, container, uploaded_file, protected=False):
        self.container = container
        self.uploaded_file = uploaded_file
        self.key = uuid.uuid4().hex
        self.protected = protected

    def call(self):
        fpath = os.path.join(
            self.FS_DIR,
            self.container,
            self.key
        )
        fdir = os.path.dirname(fpath)
        if not os.path.exists(fdir):
            os.makedirs(fdir)

        with open(fpath, 'wb') as fd:
            # TODO: Copy in chunks
            fd.write(self.uploaded_file.fd.read())

        mimetype = self.uploaded_file.headers.get('PART_CONTENT_TYPE')
        filename = self.uploaded_file.filename
        size = os.stat(fpath).st_size
        info = dict(
            filename=filename,
            physical_filepath=fpath,
            protected=self.protected
        )

        SaveMediaInfo(
            container=self.container,
            key=self.key,
            mimetype=mimetype,
            size=size,
            info=info
        ).call()

        return self.key


class SaveMediaInfo(MediaServiceBase):
    def __init__(self, container, key, mimetype, size, info):
        self.container = container
        self.key = key
        self.mimetype = mimetype
        self.size = size
        self.info = info

    def call(self):
        models.MediaFile.create(
            container=self.container,
            key=self.key,
            url='/{container}/{key}'.format(
                container=self.container, key=self.key
            ),
            uploaded_on=datetime.utcnow(),
            mimetype=self.mimetype,
            size=self.size,
            info=self.info
        )


class UpdateMediaInfo(MediaServiceBase):
    def __init__(self, container, key, info):
        self.container = container
        self.key = key
        self.info = info

    def call(self):
        media_file = models.MediaFile.objects.find_one(
            container=self.container, key=self.key)

        if media_file is not None:
            media_file.info.update(self.info)
            media_file.save(force=True)


class MediaDeleteService(MediaServiceBase):
    def __init__(self, container, key):
        self.container = container
        self.key = key

    def call(self):
        media_file = models.MediaFile.objects.find_one(
            container=self.container, key=self.key)

        if media_file is not None:
            os.unlink(media_file.info.get('physical_filepath'))
        media_file.delete()
