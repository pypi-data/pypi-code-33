from morpfw.crud.blobstorage.fsblobstorage import FSBlobStorage, FSBlob, WRITE_BUFF_SIZE
from deform.interfaces import FileUploadTempStore
import typing
from uuid import uuid4
import os
from pathlib import Path
import json
import morepath


class UIDFSBlobStorage(FSBlobStorage):

    def _uuid_path(self, uuid):
        return os.path.join(self.path, uuid)


class FSBlobFileUploadTempStore(FileUploadTempStore):

    def __init__(self, request, path):
        self.blobstorage = UIDFSBlobStorage(request, path)
        self.request = request

    def __setitem__(self, name, value):
        blob = self.blobstorage.put(
            value['fp'], filename=value['filename'], mimetype=value['mimetype'],
            uuid=name)

    def __getitem__(self, name):
        uuid = name
        blob = self.blobstorage.get(uuid)
        if blob is None:
            raise KeyError(name)
        return {
            'fp': blob.open(),
            'filename': blob.filename,
            'mimetype': blob.mimetype,
            'size': blob.get_size(),
            'uid': name
        }

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return None

    def __contains__(self, name):
        uuid = name
        blob = self.blobstorage.get(uuid)
        if blob is None:
            return False
        return True

    def preview_url(self, name):
        return None
