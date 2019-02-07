import boto3
import logging
import fnmatch
import os
from urllib import parse

logger = logging.getLogger("dativa.tools.aws.s3_lib")


class S3Location:
    """
    Class that parses out an S3 location from a passed string
    """

    _bucket = None
    _key = None

    def __init__(self, str, ignore_double_slash=False):
        result = parse.urlparse(str)

        if result.port is not None:
            raise S3ClientError("S3 URLs cannot have a port")

        if result.password is not None:
            raise S3ClientError("S3 URLs cannot have a password (or username)")

        if result.username is not None:
            raise S3ClientError("S3 URLs cannot have a username")

        if result.scheme == "":
            if result.path.startswith("/"):
                raise S3ClientError("S3 URLS must have a prefix or not start with a /, "
                                    "current val: {}".format(str))
            else:
                self._bucket = result.path.split("/")[0]
                self._key = "/".join(result.path.split("/")[1:])

        elif result.scheme == "s3":
            self._bucket = result.hostname
            self._key = result.path[1:]
        elif result.scheme in ["http", "https"]:
            if result.hostname.startswith("s3") and result.hostname.endswith(".amazonaws.com"):
                self._bucket = result.path.split("/")[1]
                self._key = "/".join(result.path.split("/")[2:])
            else:
                raise S3ClientError("S3 HTTP URLS must be of the form http[s]://s3*.amazonaws.com/bucket-name/, "
                                    "current val: {}".format(str))
        else:
            raise S3ClientError("S3 URLs must be either s3://, http://, or https://, "
                                "current val: {}".format(str))

        if not ignore_double_slash:
            if "//" in self._key:
                raise S3ClientError("S3 URLs cannot contains a // unless ignore_double_slash is set to True, "
                                    "current val: {}".format(str))

    @staticmethod
    def _coalesce_empty(s, n):
        if s == "":
            return n
        else:
            return s

    @property
    def file(self):
        return self._coalesce_empty(self._key.split("/")[-1], None)

    @property
    def prefix(self):
        if self._key is not None:
            return self._coalesce_empty("/".join(self._key.split("/")[0:-1]), None)
        else:
            return self._key

    @property
    def key(self):
        if self._key is not None:
            return self._coalesce_empty(self._key, None)
        else:
            return self._key

    @property
    def path(self):
        return self.key

    @property
    def bucket(self):
        return self._coalesce_empty(self._bucket, None)

    @property
    def s3_url(self):
        return "s3://{bucket}/{path}".format(bucket=self._bucket,
                                             path=self._key)

    def __str__(self):
        return self.s3_url

    def __repr__(self):
        return self.s3_url


class S3ClientError(Exception):
    """
    A generic class for reporting errors in the athena client
    """

    def __init__(self, reason):
        Exception.__init__(self, 'S3 Client failed: reason {}'.format(reason))
        self.reason = reason


class S3Client:
    """
    Class that provides easy access over boto s3 client
    """

    def __init__(self):
        self.s3_client = boto3.client(service_name='s3')

    def _files_within(self, directory_path, pattern):
        """
        Returns generator containing all the files in a directory
        """
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for file_name in fnmatch.filter(filenames, pattern):
                yield os.path.join(dirpath, file_name)

    def put_folder(self, source, bucket, destination="", file_format="*"):
        """
        Copies files from a directory on local system to s3
+        :param source: Folder on local filesystem that must be copied to s3
+        :param bucket: s3 bucket in which files have to be copied
+        :param destination: Location on s3 bucket to which files have to be copied
+        :param file_format: pattern for files to be transferred
+        :return: None
        """
        if os.path.isdir(source):
            file_list = list(self._files_within(source, file_format))
            for each_file in file_list:
                part_key = os.path.relpath(each_file, source)
                key = os.path.join(destination, part_key)
                self.s3_client.upload_file(each_file, bucket, key)
        else:
            raise S3ClientError("Source must be a valid directory path")

    def _generate_keys(self, bucket, prefix, suffix="", start_after=None):

        if start_after is None:
            s3_objects = self.s3_client.list_objects_v2(Bucket=bucket,
                                                        Prefix=prefix,
                                                        MaxKeys=1000)
        else:
            s3_objects = self.s3_client.list_objects_v2(Bucket=bucket,
                                                        Prefix=prefix,
                                                        MaxKeys=1000,
                                                        StartAfter=start_after)

        if 'Contents' in s3_objects:
            for key in s3_objects["Contents"]:
                if key['Key'].endswith(suffix):
                    yield key['Key']

            # get the next keys
            yield from self._generate_keys(bucket, prefix, suffix, s3_objects["Contents"][-1]['Key'])

    def delete_files(self, bucket, prefix, suffix=""):
        return self.delete("s3://{0}/{1}".format(bucket, prefix), suffix)

    def delete(self, path, suffix=""):
        loc = S3Location(path)
        keys = []
        for key in self._generate_keys(loc.bucket, loc.path, suffix):
            keys.append({'Key': key})
            if len(keys) == 1000:
                logger.info("Deleting {0} files in {1}".format(len(keys), loc.s3_url))
                self.s3_client.delete_objects(Bucket=loc.bucket,
                                              Delete={"Objects": keys})
                keys = []

        if len(keys) > 0:
            logger.info("Deleting {0} files in {1}".format(len(keys), loc.s3_url))
            self.s3_client.delete_objects(Bucket=loc.bucket,
                                          Delete={"Objects": keys})

    def list_files(self, bucket, prefix="", suffix=None, remove_prefix=False):
        return self.list("s3://{0}/{1}".format(bucket, prefix), suffix, remove_prefix)

    def list(self, path, suffix=None, remove_prefix=False):
        """
            Lists files with particular prefix/suffix stored on S3
            
            ## Parameters
            - bucket: S3 bucket in which files are stored
            - prefix: Prefix filter for files on S3
            - suffix: Suffix filter for files on S3
        """
        keys = []
        continue_flag = True
        continue_token = None

        loc = S3Location(path)

        while continue_flag:
            if continue_token:
                response = self.s3_client.list_objects_v2(Bucket=loc.bucket,
                                                          Prefix=loc.path if loc.path else "",
                                                          ContinuationToken=continue_token)
            else:
                response = self.s3_client.list_objects_v2(Bucket=loc.bucket,
                                                          Prefix=loc.path if loc.path else "")
            if response and 'Contents' in response and len(response['Contents']) > 0:
                # Get keys from response
                new_keys = map(lambda d: d['Key'], response['Contents'])
                # Filter keys by suffix
                if suffix:
                    new_keys = filter(lambda x: x.endswith(suffix), new_keys)
                # Remove prefix from keys
                if loc.path and remove_prefix:
                    new_keys = map(lambda x: x.replace(loc.path, ''), new_keys)
                # Save the keys
                keys.extend(new_keys)
                # Do we need to carry on?
                continue_flag = response['IsTruncated']
                if continue_flag and 'NextContinuationToken' in response:
                    continue_token = response['NextContinuationToken']
            else:
                continue_flag = False

        return keys
