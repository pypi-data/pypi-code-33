# coding=utf-8
from __future__ import print_function

from suanpan import path
from suanpan.arguments import Arg
from suanpan.components import Result
from suanpan.storage import storage
from suanpan.utils import csv, npy


class File(Arg):
    FILENAME = "file"
    FILETYPE = None

    def __init__(self, key, **kwargs):
        fileName = kwargs.pop("name", self.FILENAME)
        fileType = kwargs.pop("type", self.FILETYPE)
        self.fileName = (
            "{}.{}".format(fileName, fileType.lower()) if fileType else fileName
        )
        super(File, self).__init__(key, **kwargs)

    @property
    def isSet(self):
        return True

    def load(self, args):
        self.objectPrefix = super(File, self).load(args)
        self.objectName = (
            storage.pathJoin(self.objectPrefix, self.fileName)
            if self.objectPrefix
            else None
        )
        self.filePath = (
            storage.getPathInTempStore(self.objectName) if self.objectName else None
        )
        if self.filePath:
            path.safeMkdirsForFile(self.filePath)
        self.value = self.filePath
        return self.filePath

    def format(self, context):
        if self.filePath:
            storage.download(self.objectName, self.filePath)
        return self.filePath

    def save(self, context, result):
        filePath = result.value
        storage.upload(self.objectName, filePath)
        return self.objectPrefix


class Folder(Arg):
    @property
    def isSet(self):
        return True

    def load(self, args):
        self.folderName = super(Folder, self).load(args)
        self.folderPath = (
            storage.getPathInTempStore(self.folderName) if self.folderName else None
        )
        if self.folderPath:
            path.safeMkdirs(self.folderPath)
        self.value = self.folderPath
        return self.folderPath

    def format(self, context):
        if self.folderPath:
            storage.download(self.folderName, self.folderPath)
        return self.folderPath

    def clean(self, context):
        if self.folderPath:
            path.empty(self.folderPath)
        return self.folderPath

    def save(self, context, result):
        folderPath = result.value
        storage.upload(self.folderName, folderPath)
        return self.folderName


class Data(File):
    FILENAME = "data"


class Json(Data):
    FILETYPE = "json"


class Csv(Data):
    FILETYPE = "csv"

    def format(self, context):
        super(Csv, self).format(context)
        self.value = csv.load(self.filePath)
        return self.value

    def save(self, context, result):
        csv.dump(self.filePath, result.value)
        return super(Csv, self).save(context, Result(self.filePath))


class Npy(Data):
    FILETYPE = "npy"

    def format(self, context):
        super(Npy, self).format(context)
        self.value = npy.load(self.filePath)
        return self.value

    def save(self, context, result):
        npy.dump(self.filePath, result.value)
        return super(Npy, self).save(context, Result(self.filePath))


class Model(File):
    FILENAME = "model"


class H5Model(Model):
    FILETYPE = "h5"


class Checkpoint(Model):
    FILETYPE = "ckpt"


class JsonModel(Model):
    FILETYPE = "json"
