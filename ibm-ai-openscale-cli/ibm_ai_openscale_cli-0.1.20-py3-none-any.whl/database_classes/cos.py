# coding=utf-8
from ibm_botocore.client import Config
import ibm_boto3
import logging
import uuid

logger = logging.getLogger(__name__)

BUCKET_NAME_PREFIX = 'aios-fastpath-bucket-'

class CloudObjectStorage():

    def __init__(self, credentials):
        self._cos = ibm_boto3.resource("s3",
                    ibm_api_key_id=credentials['apikey'],
                    ibm_service_instance_id=credentials['resource_instance_id'],
                    ibm_auth_endpoint=credentials['iam_oidc_url'],
                    config=Config(signature_version='oauth'),
                    endpoint_url=credentials['endpoint_url'])

    def _get_existing_buckets(self):
        try:
            logger.debug("Retrieving list of existing buckets from IBM Cloud Object Storage ...")
            return self._cos.buckets.all()
        except Exception as e:
            logger.error("Unable to retrieve list buckets: {}".format(e))

    def get_bucket(self):
        buckets = self._get_existing_buckets()
        for bucket in buckets:
            if bucket.name.startswith(BUCKET_NAME_PREFIX):
                logger.info("Found bucket: {}".format(bucket.name))
                return bucket
        return None

    def create_bucket(self):
        bucket_name = BUCKET_NAME_PREFIX + str(uuid.uuid4())
        logger.info("Creating new bucket: {}".format(bucket_name))
        try:
            return self._cos.Bucket(bucket_name).create()
            logger.info("Bucket: {} created!".format(bucket_name))
        except Exception as e:
            logger.error("Unable to create bucket: {}".format(e))

    def delete_item(self, bucket_name, item_name):
        try:
            logger.info("Deleting item: {} from bucket: {}".format(item_name, bucket_name))
            self._cos.Object(bucket_name, item_name).delete()
            logger.info("Item: {} deleted!".format(item_name))
        except Exception as e:
            logger.error("Unable to delete item: {}".format(e))

    def multi_part_upload(self, bucket_name, item_name, file_path):
        try:
            logger.info("Uploading item: {} to bucket: {}".format(item_name, bucket_name))
            # set 5 MB chunks and threadhold to 15 MB
            part_size = 1024 * 1024 * 5
            file_threshold = 1024 * 1024 * 15
            transfer_config = ibm_boto3.s3.transfer.TransferConfig(
                multipart_threshold=file_threshold,
                multipart_chunksize=part_size
            )
            with open(file_path, "rb") as file_data:
                self._cos.Object(bucket_name, item_name).upload_fileobj(
                    Fileobj=file_data,
                    Config=transfer_config
                )
            logger.info("Uploaded: {}!".format(item_name))
        except Exception as e:
            logger.error("Unable to upload item: {}".format(e))