from google.cloud import storage
import time, base64

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

####################################################################################################
#
# Manager for interactions with Google Cloud Storage
#
####################################################################################################

class google_cloud_storage_io(object):

    _certificate_filename = 'certificates/aether-google-cloud-storage-35700bb84743.json'

    def __init__(self):
        self._client = storage.Client.from_service_account_json(self._certificate_filename)

    def blob_exists(self, bucket_name, blob_name):
        """Returns True if a blob exists."""
        bucket = self._client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.exists()

    def upload_blob(self, bucket_name, source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        bucket = self._client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        s = time.time()
        logger.info('Uploading {} to {}.'.format(source_file_name, bucket_name))
        blob.upload_from_filename(source_file_name)
        logger.info('File uploaded, duration: {}'.format(time.time() - s))

    def download_blob(self, bucket_name, source_blob_name, destination_file_name):
        """Downloads a blob from the bucket."""
        bucket = self._client.get_bucket(bucket_name)
        blob = bucket.blob(source_blob_name)

        s = time.time()
        logger.info('Downloading {} to {}.'.format(source_blob_name, destination_file_name))
        blob.download_to_filename(destination_file_name)
        logger.info('File downloaded, duration: {}.'.format(time.time() - s))

    def add_user_owner_policy_to_object(self, bucket_name, destination_blob_name, user_email_address, role='roles/storage.objectAdmin'):
        """Adds ownership policy to a blob from the bucket."""
        bucket = self._client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        policy = blob.get_iam_policy()
        policy[role].add("user:{}".format(user_email_address))
        logger.info('Adding {} with role {} from {} in bucket {}.'.format(user_email_address, role, destination_blob_name, bucket_name))
        blob.set_iam_policy(policy)

    def remove_user_owner_policy_to_object(self, bucket_name, destination_blob_name, user_email_address, role='roles/storage.objectAdmin'):
        """Removes ownership policy from a blob from the bucket."""
        bucket = self._client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        policy = blob.get_iam_policy()
        policy[role].discard("user:{}".format(user_email_address))
        logger.info('Removing {} with role {} from {} in bucket {}.'.format(user_email_address, role, destination_blob_name, bucket_name))
        blob.set_iam_policy(policy)

