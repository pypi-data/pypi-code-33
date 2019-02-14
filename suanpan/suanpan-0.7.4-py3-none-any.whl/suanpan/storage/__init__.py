# coding=utf-8
from __future__ import print_function

from suanpan.arguments import Int, String
from suanpan.storage.oss import OssStorage
from suanpan.proxy import Proxy
import tempfile


class StorageProxy(Proxy):
    MAPPING = {"oss": OssStorage}
    ARGUMENTS = [
        String("storage-type", default="oss"),
        String("storage-oss-access-id"),
        String("storage-oss-access-key"),
        String("storage-oss-bucket-name", default="suanpan"),
        String("storage-oss-endpoint", default="http://oss-cn-beijing.aliyuncs.com"),
        String("storage-oss-delimiter", default="/"),
        String("storage-oss-temp-store", default=tempfile.gettempdir()),
        Int("storage-oss-download-num-threads", default=1),
        String("storage-oss-download-store-name", default=".py-oss-download"),
        Int("storage-oss-upload-num-threads", default=1),
        String("storage-oss-upload-store-name", default=".py-oss-upload"),
    ]


storage = StorageProxy()
