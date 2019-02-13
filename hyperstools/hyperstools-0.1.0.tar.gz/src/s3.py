# encoding: utf-8
import six

import boto3


class S3(object):

    """S3客户端封装"""

    def __init__(
        self,
        host=None,
        port=None,
        access_key=None,
        secret_key=None,
        bucket=None,
        key=None,
        secure=True,
    ):
        """TODO: to be defined1.

        :host: TODO
        :port: TODO
        :access_key: TODO
        :secret_key: TODO
        :bucket: TODO
        :key: TODO

        """
        self._bucket = bucket
        self._key = key

        _protocol = secure and "https://" or "http://"
        self._host = _protocol + host

        session = boto3.session.Session()
        self._client = session.client(
            service_name="s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=self._host,
        )

    @property
    def url(self):
        return self._host + "/" + self._bucket + "/" + self._key

    def download(self, key, path=None):
        """下载S3文件

        :key: S3上的路径
        :path: 下载到的本地路径，如果为空，则返回bytesio
        :returns: file like obj

        """
        if path:
            return self._client.download_file(self._bucket, key, path)
        bio = six.BytesIO()
        return self._client.download_fileobj(self._bucket, key, bio)

    def upload(self, path, key, perm=None):
        """上传S3文件

        :path: 下载到的本地路径，如果为空，则返回bytesio
        :key: S3上的路径
        :perm: 权限 public| private
        :returns: file like obj

        """
        if path:
            return self._client.upload_file(path, self._bucket, key)
        bio = six.BytesIO()
        return self._client.upload_fileobj(bio, self._bucket, key)

    def putACL(self, key, ACL):
        """设置文件权限

        :key: S3上文件路径
        :ACL: private|public-read
        """
        self._client.put_object_acl(ACL=ACL, Bucket=self._bucket, Key=key)
