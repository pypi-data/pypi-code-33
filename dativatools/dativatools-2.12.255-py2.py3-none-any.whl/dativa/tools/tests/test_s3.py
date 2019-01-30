import unittest
import logging
from dativa.tools.aws import S3Location, S3ClientError


logger = logging.getLogger("dativa.tools.aws.tests.s3")


# noinspection SqlNoDataSourceInspection
class S3Test(unittest.TestCase):

    def test_s3_url(self):
        loc = S3Location("s3://bucket/path/file")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/file", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertEqual("file", loc.file)
        self.assertEqual("s3://bucket/path/file", loc.s3_url)

    def test_s3_url_folder(self):
        loc = S3Location("s3://bucket/path/")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/path/", loc.s3_url)

    def test_has_port(self):
        with self.assertRaises(S3ClientError):
            loc = S3Location("s3://bucket:90/path/")

    def test_has_user(self):
        with self.assertRaises(S3ClientError):
            loc = S3Location("s3://user@bucket/path/")

    def test_has_password(self):
        with self.assertRaises(S3ClientError):
            loc = S3Location("s3://user:password@bucket/path/")

    def test_has_slash(self):
        with self.assertRaises(S3ClientError):
            loc = S3Location("/bucket")

    def test_bare_bucket(self):
        loc = S3Location("bucket")
        self.assertEqual("bucket", loc.bucket)
        self.assertIsNone(loc.path)
        self.assertIsNone(loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/", loc.s3_url)

    def test_bare_bucket_slash(self):
        loc = S3Location("bucket/")
        self.assertEqual("bucket", loc.bucket)
        self.assertIsNone(loc.path)
        self.assertIsNone(loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/", loc.s3_url)

    def test_bare_bucket_path(self):
        loc = S3Location("bucket/path")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path", loc.path)
        self.assertIsNone(loc.prefix)
        self.assertEqual("path", loc.file)
        self.assertEqual("s3://bucket/path", loc.s3_url)

    def test_http_bucket(self):
        loc = S3Location("http://s3.amazonaws.com/bucket/")
        self.assertEqual("bucket", loc.bucket)
        self.assertIsNone(loc.path)
        self.assertIsNone(loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/", loc.s3_url)

    def test_http_bucket_path(self):
        loc = S3Location("http://s3.amazonaws.com/bucket/path")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path", loc.path)
        self.assertIsNone(loc.prefix)
        self.assertEqual("path", loc.file)
        self.assertEqual("s3://bucket/path", loc.s3_url)

    def test_http_bucket_path_slash(self):
        loc = S3Location("http://s3-us-west-1.amazonaws.com/bucket/path/")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/path/", loc.s3_url)

    def test_http_bucket_path_file(self):
        loc = S3Location("http://s3-us-west-1.amazonaws.com/bucket/path/file")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/file", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertEqual("file", loc.file)
        self.assertEqual("s3://bucket/path/file", loc.s3_url)

    def test_https_bucket(self):
        loc = S3Location("https://s3-us-west-1.amazonaws.com/bucket/")
        self.assertEqual("bucket", loc.bucket)
        self.assertIsNone(loc.path)
        self.assertIsNone(loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/", loc.s3_url)

    def test_https_bucket_path(self):
        loc = S3Location("https://s3-us-west-1.amazonaws.com/bucket/path")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path", loc.path)
        self.assertIsNone(loc.prefix)
        self.assertEqual("path", loc.file)
        self.assertEqual("s3://bucket/path", loc.s3_url)

    def test_https_bucket_path_slash(self):
        loc = S3Location("https://s3-us-east-1.amazonaws.com/bucket/path/")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertIsNone(loc.file)
        self.assertEqual("s3://bucket/path/", loc.s3_url)

    def test_https_bucket_path_file(self):
        loc = S3Location("https://s3.amazonaws.com/bucket/path/file")
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("path/file", loc.path)
        self.assertEqual("path", loc.prefix)
        self.assertEqual("file", loc.file)
        self.assertEqual("s3://bucket/path/file", loc.s3_url)

    def test_https_invalid(self):
        with self.assertRaises(S3ClientError):
            S3Location("https://amazonaws.com/bucket/path/file")

    def test_https_invalid_2(self):
        with self.assertRaises(S3ClientError):
            S3Location("https://s3-amazonaws.com/bucket/path/file")

    def test_news(self):
        with self.assertRaises(S3ClientError):
            S3Location("news://s3-amazonaws.com/bucket/path/file")

    def test_double_slash(self):
        with self.assertRaises(S3ClientError):
            S3Location("s3://bucket/path//file")
