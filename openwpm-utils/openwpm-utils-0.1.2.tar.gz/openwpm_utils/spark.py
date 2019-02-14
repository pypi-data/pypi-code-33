import jsbeautifier
import boto3
import gzip
import io
from botocore.exceptions import ClientError

S3_ROOT = 's3a://openwpm-crawls'

class S3Dataset(object):
    def __init__(self, crawl_directory):
      self._s3_table_loc = "s3a://%s/%s/visits/%%s/" % (S3_ROOT, crawl_directory)
      self._s3_content_loc = "%s/%s/content/%%s.gz" % (S3_ROOT, crawl_directory)

    def read_table(self, table_name, columns=None):
        table = sqlContext.read.parquet(self._s3_table_loc % table_name)
        if columns is not None:
            return table.select(columns)
        return table

    def read_content(self, content_hash):
        """Read the content corresponding to `content_hash`.

        NOTE: This can only be run in the driver process since it uses the spark context
        """
        return sc.textFile(self._s3_content_loc % content_hash)

    def collect_content(self, content_hash, beautify=False):
        """Collect content for `content_hash` to driver

        NOTE: This can only be run in the driver process since it uses the spark context
        """
        content = ''.join(self.read_content(content_hash).collect())
        if beautify:
            return jsbeautifier.beautify(content)
        return content


class WorkerSafeS3Dataset(object):
    """This class is a helper to allow worker processes to access the S3 dataset.

    Workers can not use the spark context directly. This class should include no
    references to the spark context so it can be serialized and sent to workers.
    """
    def __init__(self, crawl_directory):
        self._bucket = S3_ROOT.split('//')[1]
        self._key = "%s/content/%%s.gz" % crawl_directory

    def collect_content(self, content_hash, beautify=False):
        """Collect content in worker process.

        See: https://github.com/databricks/spark-deep-learning/issues/67#issuecomment-340089028
             for a description of why it's faster to use this than to loop through `read_content`
             in the driver process and then distribute those handles to the worker processes.
        """
        s3 = boto3.client('s3')
    try:
      obj = s3.get_object(
        Bucket=self._bucket,
        Key=self._key % content_hash
      )
      body = obj["Body"]
      compressed_content = io.BytesIO(body.read())
      body.close()
    except ClientError as e:
      if e.response['Error']['Code'] != 'NoSuchKey':
        raise
      else:
        return None

    with gzip.GzipFile(fileobj=compressed_content, mode='r') as f:
      content = f.read()

    if content is None or content == "":
      return ""

    if beautify:
      try:
        content = jsbeautifier.beautify(content)
      except IndexError:
        pass
    try:
      return content.decode('utf-8')
    except ValueError:
      return content.decode('utf-8', errors='ignore')
