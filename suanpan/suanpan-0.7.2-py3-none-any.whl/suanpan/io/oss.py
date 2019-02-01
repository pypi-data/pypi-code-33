# coding=utf-8
from __future__ import division, print_function

import functools
import math
import os
import shutil
import time
import zipfile

import oss2
import tqdm
from oss2.models import PartInfo
from oss2.resumable import ResumableDownloadStore, ResumableStore
from retrying import retry

from suanpan import asyncio, path
from suanpan.log import logger


class FrequenceTimeLimiter(object):
    def __init__(self, seconds):
        self.frequence = seconds
        self.time = time.time()

    def ifEnable(self):
        newTime = time.time()
        enable = self.frequence < newTime - self.time
        self.time = newTime if enable else self.time
        return enable


class OssStorage(object):

    DEFAULT_IGNORE_KEYWORDS = {"__MACOSX", ".DS_Store"}
    CONTENT_MD5 = "Content-MD5"

    LARGE_FILE_SIZE = 1024 * 1024 * 1024  # 1GB
    PREFERRED_SIZE = 500 * 1024 * 1024  # 500MB

    PBAR_FORMAT = "{l_bar}{bar}"

    def __init__(
        self,
        ossAccessId,
        ossAccessKey,
        ossBucketName="suanpan",
        ossEndpoint="http://oss-cn-beijing.aliyuncs.com",
        ossDelimiter="/",
        ossTempStore="/tmp",
        ossDownloadNumThreads=1,
        ossDownloadStoreName=".py-oss-download",
        ossUploadNumThreads=1,
        ossUploadStoreName=".py-oss-upload",
        **kwargs
    ):
        self.accessId = ossAccessId
        self.accessKey = ossAccessKey
        self.bucketName = ossBucketName
        self.endpoint = ossEndpoint

        self.auth = oss2.Auth(self.accessId, self.accessKey)
        self.bucket = self.getBucket(self.bucketName)

        self.delimiter = ossDelimiter
        self.tempStore = ossTempStore

        self.downloadNumThreads = ossDownloadNumThreads
        self.downloadStoreName = ossDownloadStoreName
        self.downloadStore = ResumableDownloadStore(
            self.tempStore, self.downloadStoreName
        )

        self.uploadNumThreads = ossUploadNumThreads
        self.uploadStoreName = ossUploadStoreName
        self.uploadStore = ResumableStore(self.tempStore, self.uploadStoreName)

        self.removeOssLogger()

    def removeOssLogger(self):
        ossLogger = getattr(oss2, "logger", None)
        if ossLogger:
            self.removeLoggerHandlers(ossLogger)

    def removeLoggerHandlers(self, logger):
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        return logger

    def getBucket(self, bucketOrBucketName):
        return (
            bucketOrBucketName
            if isinstance(bucketOrBucketName, oss2.Bucket)
            else self.getBucketByName(bucketOrBucketName)
        )

    def getBucketByName(self, bucketName=None):
        return (
            oss2.Bucket(self.auth, self.endpoint, bucketName)
            if bucketName
            else self.bucket
        )

    def downloadIntoTempStore(
        self,
        name,
        path=None,
        tempStore=None,
        bucketOrBucketName=None,
        ignore=DEFAULT_IGNORE_KEYWORDS,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        path = path or self.localPathJoin(bucket.bucket_name, name)
        path = self.getPathInTempStore(path, tempStore=tempStore)
        return self.download(name, path, bucketOrBucketName=bucket, ignore=ignore)

    def download(
        self, name, path, bucketOrBucketName=None, ignore=DEFAULT_IGNORE_KEYWORDS
    ):
        bucket = self.getBucket(bucketOrBucketName)
        downloadFunction = (
            self.downloadFile
            if self.isFile(name, bucketOrBucketName=bucket)
            else self.downloadFolder
        )
        return downloadFunction(name, path, bucketOrBucketName=bucket, ignore=ignore)

    @retry(stop_max_attempt_number=3)
    def downloadFile(
        self,
        objectName,
        filePath,
        bucketOrBucketName=None,
        ignore=DEFAULT_IGNORE_KEYWORDS,
        quiet=False,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        storagePath = self.storageUrl(bucket, objectName)
        fileSize = bucket.head_object(objectName).content_length

        if not quiet:
            logger.info("Downloading file: {} -> {}".format(storagePath, filePath))

        with tqdm.tqdm(
            total=fileSize, bar_format=self.PBAR_FORMAT, disable=quiet
        ) as pbar:
            if filePath in ignore:
                pbar.update(fileSize)
                pbar.set_description("Ignored")
                return filePath

            if self.checkMd5(objectName, filePath, bucketOrBucketName=bucket):
                pbar.update(fileSize)
                pbar.set_description("Existed")
                return filePath

            def _percentage(consumed_bytes, total_bytes):
                if total_bytes:
                    pbar.update(consumed_bytes - pbar.n)
                    pbar.set_description("Downloading")

            path.safeMkdirsForFile((filePath))
            oss2.resumable_download(
                bucket,
                objectName,
                filePath,
                num_threads=self.downloadNumThreads,
                store=self.downloadStore,
                progress_callback=_percentage,
            )

            pbar.set_description("Downloaded")

            return filePath

    def downloadFolder(
        self,
        folderName,
        folderPath,
        delimiter=None,
        bucketOrBucketName=None,
        workers=None,
        ignore=DEFAULT_IGNORE_KEYWORDS,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        delimiter = delimiter or self.delimiter
        storagePath = self.storageUrl(bucket, folderName)

        if folderPath in ignore:
            logger.info(
                "Ignore downloading folder: {} -> {}".format(folderPath, storagePath)
            )
            return folderPath

        downloads = {
            file: self.localPathJoin(folderPath, self.ossRelativePath(file, folderName))
            for _, _, files in self.walk(
                folderName, delimiter=delimiter, bucketOrBucketName=bucket
            )
            for file in files
        }

        logger.info("Downloading folder: {} -> {}".format(storagePath, folderPath))
        # Download from oss
        _run = functools.partial(
            self.downloadFile, bucketOrBucketName=bucket, ignore=ignore, quiet=True
        )
        asyncio.starmap(_run, downloads.items(), pbar="Downloading", thread=True)
        # Remove ignore
        self.removeIgnore(folderPath, ignore=ignore)
        # Remove rest files and folders
        files = (
            os.path.join(root, file)
            for root, _, files in os.walk(folderPath)
            for file in files
        )
        restFiles = [file for file in files if file not in downloads.values()]
        asyncio.map(
            path.remove,
            restFiles,
            pbar="Removing Rest Files" if restFiles else False,
            thread=True,
        )
        path.removeEmptyFolders(folderPath)
        logger.info("Removed empty folders in: {}".format(folderPath))
        # End
        logger.info("Downloaded folder: {} -> {}".format(storagePath, folderPath))
        return folderPath

    def uploadFromTempStore(
        self,
        name,
        path=None,
        tempStore=None,
        bucketOrBucketName=None,
        ignore=DEFAULT_IGNORE_KEYWORDS,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        path = path or self.localPathJoin(bucket.bucket_name, name)
        path = self.getPathInTempStore(path, tempStore=tempStore)
        return self.upload(name, path, bucketOrBucketName=bucket, ignore=ignore)

    def upload(
        self, name, path, bucketOrBucketName=None, ignore=DEFAULT_IGNORE_KEYWORDS
    ):
        bucket = self.getBucket(bucketOrBucketName)
        uploadFunction = self.uploadFolder if os.path.isdir(path) else self.uploadFile
        return uploadFunction(name, path, bucketOrBucketName=bucket, ignore=ignore)

    def uploadFile(
        self,
        objectName,
        filePath,
        bucketOrBucketName=None,
        ignore=DEFAULT_IGNORE_KEYWORDS,
        quiet=False,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        storagePath = self.storageUrl(bucket, objectName)
        fileSize = os.path.getsize(filePath)

        if not quiet:
            logger.info("Uploading file: {} -> {}".format(filePath, storagePath))
        with tqdm.tqdm(
            total=fileSize, bar_format=self.PBAR_FORMAT, disable=quiet
        ) as pbar:

            if filePath in ignore:
                pbar.update(fileSize)
                pbar.set_description("Ignored")
                return filePath

            fileMd5 = path.md5(filePath)
            if self.getMd5(objectName, bucketOrBucketName=bucket) == fileMd5:
                pbar.update(fileSize)
                pbar.set_description("Existed")
                return filePath

            def _percentage(consumed_bytes, total_bytes):
                if total_bytes:
                    pbar.update(consumed_bytes - pbar.n)
                    pbar.set_description("Uploading")

            oss2.resumable_upload(
                bucket,
                objectName,
                filePath,
                num_threads=self.uploadNumThreads,
                store=self.uploadStore,
                progress_callback=_percentage,
                headers={self.CONTENT_MD5: fileMd5},
            )

            pbar.set_description("Uploaded")

            return filePath

    def uploadFolder(
        self,
        folderName,
        folderPath,
        bucketOrBucketName=None,
        workers=None,
        ignore=DEFAULT_IGNORE_KEYWORDS,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        storagePath = self.storageUrl(bucket, folderName)

        if folderName in ignore:
            logger.info(
                "Ignore uploading folder: {} -> {}".format(folderName, storagePath)
            )
            return folderPath

        filePaths = (
            os.path.join(root, file)
            for root, _, files in os.walk(folderPath)
            for file in files
        )
        uploads = {
            filePath: self.ossPathJoin(
                folderName, self.localRelativePath(filePath, folderPath)
            )
            for filePath in filePaths
        }

        if not uploads:
            logger.warning("Uploading empty folder: {}".format(folderPath))
            return folderPath

        logger.info("Uploading folder: {} -> {}".format(folderPath, storagePath))
        # Upload files to oss
        uploadItems = [
            (objectName, filePath) for filePath, objectName in uploads.items()
        ]
        _run = functools.partial(
            self.uploadFile, bucketOrBucketName=bucket, ignore=ignore, quiet=True
        )
        asyncio.starmap(_run, uploadItems, pbar="Uploading", thread=True)
        # Remove rest files
        localFiles = set(
            self.localRelativePath(filePath, folderPath) for filePath in uploads.keys()
        )
        remoteFiles = set(
            self.ossRelativePath(objectName, folderName)
            for _, _, files in self.walk(folderName)
            for objectName in files
        )
        restFiles = [
            self.ossPathJoin(folderName, file) for file in remoteFiles - localFiles
        ]
        _run = functools.partial(self.remove, bucketOrBucketName=bucket, quiet=True)
        asyncio.map(
            _run,
            restFiles,
            pbar="Removing Rest Files" if restFiles else False,
            thread=True,
        )
        # End
        logger.info("Uploaded folder: {} -> {}".format(folderPath, storagePath))
        return folderPath

    def walk(self, folderName, delimiter=None, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        delimiter = delimiter or self.delimiter
        root = folderName if folderName.endswith(delimiter) else folderName + delimiter
        folders = []
        files = []
        for obj in oss2.ObjectIterator(bucket, delimiter=delimiter, prefix=root):
            array = folders if obj.is_prefix() else files
            array.append(obj.key)
        if not folders and not files:
            storagePath = self.storageUrl(bucket, root)
            raise Exception("Oss Error: No such folder: {}".format(storagePath))
        yield root, folders, files
        for folder in folders:
            for item in self.walk(
                folder, delimiter=delimiter, bucketOrBucketName=bucket
            ):
                yield item

    def listAll(self, folderName, delimiter=None, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        delimiter = delimiter or self.delimiter
        prefix = (
            folderName if folderName.endswith(delimiter) else folderName + delimiter
        )
        return (
            obj
            for obj in oss2.ObjectIterator(
                delimiter=delimiter, prefix=prefix, bucket=bucket
            )
        )

    def listFolders(self, folderName, delimiter=None, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        delimiter = delimiter or self.delimiter
        return (
            obj
            for obj in self.listAll(
                folderName, delimiter=delimiter, bucketOrBucketName=bucket
            )
            if obj.is_prefix()
        )

    def listFiles(self, folderName, delimiter=None, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        delimiter = delimiter or self.delimiter
        return (
            obj
            for obj in self.listAll(
                folderName, delimiter=delimiter, bucketOrBucketName=bucket
            )
            if not obj.is_prefix()
        )

    def isFile(self, objectName, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        return bucket.object_exists(objectName)

    def isFolder(self, folderName, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        return next(self.listAll(folderName, bucketOrBucketName=bucket), None)

    def getPathInTempStore(self, path, tempStore=None):
        tempStore = tempStore or self.tempStore
        return self.localPathJoin(tempStore, path)

    def toLocalPath(self, objectName, delimiter=None):
        delimiter = delimiter or self.delimiter
        return objectName.replace(delimiter, os.sep)

    def toOssPath(self, path, delimiter=None):
        delimiter = delimiter or self.delimiter
        return path.replace(os.sep, delimiter)

    def localPathJoin(self, *paths):
        path = os.path.join(*paths)
        return self.toLocalPath(path)

    def ossPathJoin(self, *paths):
        path = os.path.join(*paths)
        return self.toOssPath(path)

    def pathJoin(self, *paths, **kwargs):
        mode = kwargs.get("mode", "oss")
        return self.ossPathJoin(*paths) if mode == "oss" else self.localPathJoin(*paths)

    def localRelativePath(self, path, base):
        return self.relativePath(path, base, delimiter=os.sep)

    def ossRelativePath(self, path, base, delimiter=None):
        delimiter = delimiter or self.delimiter
        return self.relativePath(path, base, delimiter=delimiter)

    def relativePath(self, path, base, delimiter):
        base = base if base.endswith(delimiter) else base + delimiter
        return path[len(base) :] if path.startswith(base) else path

    def compress(self, zipFilePath, path, ignore=DEFAULT_IGNORE_KEYWORDS):
        compressFunc = self.compressFolder if os.path.isdir(path) else self.compressFile
        return compressFunc(zipFilePath, path)

    def compressFolder(self, zipFilePath, folderPath, ignore=DEFAULT_IGNORE_KEYWORDS):
        if folderPath in ignore:
            logger.info(
                "Ignore compressing folder: {} -> {}".format(folderPath, zipFilePath)
            )
            return zipFilePath

        logger.info("Compressing folder: {} -> {}".format(folderPath, zipFilePath))
        with zipfile.ZipFile(zipFilePath, "w") as zip:
            for root, _, files in os.walk(folderPath):
                for file in files:
                    filePath = os.path.join(root, file)
                    zip.write(
                        filePath, arcname=self.localRelativePath(filePath, folderPath)
                    )
        logger.info("Compressed folder: {} -> {}".format(folderPath, zipFilePath))
        return zipFilePath

    def compressFile(self, zipFilePath, filePath, ignore=DEFAULT_IGNORE_KEYWORDS):
        if filePath in ignore:
            logger.info(
                "Ignore compressing File: {} -> {}".format(filePath, zipFilePath)
            )
            return zipFilePath

        logger.info("Compressing File: {} -> {}".format(filePath, zipFilePath))
        with zipfile.ZipFile(zipFilePath, "w") as zip:
            _, filename = os.path.split(filePath)
            zip.write(filePath, arcname=filename)
        logger.info("Compressed File: {} -> {}".format(filePath, zipFilePath))
        return zipFilePath

    def extract(self, zipFilePath, distPath, ignore=DEFAULT_IGNORE_KEYWORDS):
        logger.info("Extracting zip: {} -> {}".format(zipFilePath, distPath))
        with zipfile.ZipFile(zipFilePath, "r") as zip:
            zip.extractall(distPath)
        self.removeIgnore(distPath, ignore=ignore)
        logger.info("Extracted zip: {} -> {}".format(zipFilePath, distPath))

    def remove(self, objectName, delimiter=None, bucketOrBucketName=None, quiet=False):
        delimiter = delimiter or self.delimiter
        bucket = self.getBucket(bucketOrBucketName)
        removeFunc = (
            self.removeFile
            if self.isFile(objectName, bucketOrBucketName=bucket)
            else self.removeFolder
        )
        return removeFunc(
            objectName, delimiter=delimiter, bucketOrBucketName=bucket, quiet=quiet
        )

    def removeFile(
        self, fileName, delimiter=None, bucketOrBucketName=None, quiet=False
    ):
        bucket = self.getBucket(bucketOrBucketName)
        bucket.delete_object(fileName)
        storagePath = self.storageUrl(bucket, fileName)
        if not quiet:
            logger.info("Removed file: {}".format(storagePath))
        return fileName

    def removeFolder(
        self, folderName, delimiter=None, bucketOrBucketName=None, quiet=False
    ):
        delimiter = delimiter or self.delimiter
        bucket = self.getBucket(bucketOrBucketName)
        folderName = (
            folderName + delimiter if not folderName.endswith(delimiter) else folderName
        )
        removes = [
            objectName for _, _, files in self.walk(folderName) for objectName in files
        ]
        _run = functools.partial(
            self.remove, delimiter=delimiter, bucketOrBucketName=bucket, quiet=True
        )
        asyncio.map(
            _run,
            removes,
            pbar="Removing" if removes and not quiet else False,
            thread=True,
        )
        return folderName

    def storageUrl(self, bucket, path):
        return "oss:///" + self.ossPathJoin(bucket.bucket_name, path)

    def removeIgnore(self, path, ignore=DEFAULT_IGNORE_KEYWORDS):
        def _ignore(_root, _path):
            if _path in ignore:
                _path = os.path.join(_root, _path)
                if os.path.isfile(_path):
                    os.remove(_path)
                    logger.info("Removed ignore file: {}".format(_path))
                else:
                    shutil.rmtree(_path)
                    logger.info("Removed ignore folder: {}".format(_path))

        for root, folders, files in os.walk(path):
            for folder in folders:
                _ignore(root, folder)
            for file in files:
                _ignore(root, file)

    def getMd5(self, objectName, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        try:
            return bucket.head_object(objectName).headers.get(self.CONTENT_MD5)
        except:
            return None

    def checkMd5(self, objectName, filePath, bucketOrBucketName=None):
        if not os.path.isfile(filePath):
            return False

        bucket = self.getBucket(bucketOrBucketName)
        return self.getMd5(objectName, bucketOrBucketName=bucket) == path.md5(filePath)

    def checkObjectMd5(self, objectNameA, objectNameB, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        md5a, md5b = (
            self.getMd5(objectNameA, bucketOrBucketName=bucket),
            self.getMd5(objectNameB, bucketOrBucketName=bucket),
        )
        return md5a == md5b and md5a is not None

    def copy(self, name, dist, bucketOrBucketName=None):
        bucket = self.getBucket(bucketOrBucketName)
        copyFunction = (
            self.copyFile
            if self.isFile(name, bucketOrBucketName=bucket)
            else self.copyFolder
        )
        return copyFunction(name, dist, bucketOrBucketName=bucket)

    def copyFolder(
        self,
        folderName,
        distName,
        bucketOrBucketName=None,
        workers=None,
        delimiter=None,
    ):
        bucket = self.getBucket(bucketOrBucketName)
        delimiter = delimiter or self.delimiter
        folderName = (
            folderName if folderName.endswith(delimiter) else folderName + delimiter
        )
        distName = distName if distName.endswith(delimiter) else distName + delimiter
        logger.info("Copying folder: {} -> {}".format(folderName, distName))
        copyItems = [
            (file, file.replace(folderName, distName))
            for _, _, files in self.walk(
                folderName, delimiter=delimiter, bucketOrBucketName=bucket
            )
            for file in files
        ]
        _run = functools.partial(self.copyFile, bucketOrBucketName=bucket, quiet=True)
        asyncio.starmap(_run, copyItems, pbar="Copying", thread=True)

    def copyFile(self, objectName, distName, bucketOrBucketName=None, quiet=False):
        bucket = self.getBucket(bucketOrBucketName)
        fileSize = bucket.head_object(objectName).content_length
        copyFunction = (
            self.copyLargeFile
            if fileSize >= self.LARGE_FILE_SIZE
            else self.copySmallFile
        )
        return copyFunction(
            objectName, distName, fileSize, bucketOrBucketName=bucket, quiet=quiet
        )

    def copySmallFile(
        self, objectName, distName, size, bucketOrBucketName=None, quiet=False
    ):
        bucket = self.getBucket(bucketOrBucketName)

        if not quiet:
            logger.info(
                "Copying file: {} -> {}".format(
                    self.storageUrl(bucket, objectName),
                    self.storageUrl(bucket, distName),
                )
            )

        with tqdm.tqdm(total=size, bar_format=self.PBAR_FORMAT, disable=quiet) as pbar:
            if self.checkObjectMd5(objectName, distName, bucketOrBucketName=bucket):
                pbar.update(size)
                pbar.set_description("Existed")
                return distName

            bucket.copy_object(bucket.bucket_name, objectName, distName)
            pbar.update(size)
            return distName

    def copyLargeFile(
        self, objectName, distName, size, bucketOrBucketName=None, quiet=False
    ):
        bucket = self.getBucket(bucketOrBucketName)

        if not quiet:
            logger.info(
                "Copying file: {} -> {}".format(
                    self.storageUrl(bucket, objectName),
                    self.storageUrl(bucket, distName),
                )
            )

        with tqdm.tqdm(total=size, bar_format=self.PBAR_FORMAT, disable=quiet) as pbar:
            if self.checkObjectMd5(objectName, distName, bucketOrBucketName=bucket):
                pbar.update(size)
                pbar.set_description("Existed")
                return distName

            partSize = oss2.determine_part_size(
                size, preferred_size=self.PREFERRED_SIZE
            )
            uploadId = bucket.init_multipart_upload(distName).upload_id
            parts = math.ceil(size / partSize)
            parts = (
                (i + 1, i * partSize, min((i + 1) * partSize, size))
                for i in range(parts)
            )

            def _copy(part):
                partNumber, byteRange = part[0], part[-2:]
                result = bucket.upload_part_copy(
                    bucket.bucket_name,
                    objectName,
                    byteRange,
                    distName,
                    uploadId,
                    partNumber,
                )
                pbar.update(byteRange[1] - byteRange[0])
                return PartInfo(partNumber, result.etag)

            parts = [_copy(part) for part in parts]
            bucket.complete_multipart_upload(distName, uploadId, parts)
            return distName

    def pathSplit(self, objectName, delimiter=None):
        delimiter = delimiter or self.delimiter
        return objectName.rsplit(delimiter, 1)

    def pathSplitExt(self, objectName, extDelimiter="."):
        return objectName.rsplit(extDelimiter, 1)

    def pbarRunner(self, pbar, quantity=1):
        def _dec(runner):
            @functools.wraps(runner)
            def _runner(*args, **kwargs):
                result = runner(*args, **kwargs)
                pbar.update(quantity)
                return result

            return _runner

        return _dec
