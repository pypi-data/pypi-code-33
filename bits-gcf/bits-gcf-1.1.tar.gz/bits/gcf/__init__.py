"""Google Cloud Functions helper classes."""

import base64
import datetime
import json

from google.cloud import pubsub_v1
from google.cloud import storage


class Google(object):
    """Google Class."""

    def generate_json_object_name(self, base, prefix):
        """Return an object name for a new JSON file in GCS."""
        # get current date in iso format
        now = datetime.datetime.now()
        isodate = datetime.datetime.isoformat(now)

        # create object name
        name = '%s/%s_%s.json' % (
            base,
            prefix,
            isodate,
        )

        return name

    def get_pubsub_message_json_data(self, data):
        """Return the json body from the pubsub message."""
        # get the body text
        body_text = None
        if 'data' in data:
            body_text = base64.b64decode(data['data']).decode('utf-8')

        # convert the text to json
        message_data = None
        if body_text:
            message_data = json.loads(body_text)

        return message_data

    def notify_pubsub(
        self,
        project,
        topic,
        bodyString,
    ):
        """Send a PubSub notifiction to a specific project/topic."""
        # format the message data
        data = (u'%s' % (bodyString)).encode('utf-8')

        # create publisher
        publisher = pubsub_v1.PublisherClient()

        # create topic path
        topic_path = publisher.topic_path(project, topic)

        # create a future to publish the message
        future = publisher.publish(topic_path, data=data)

        # log the message
        print('Published "%s" to %s as message %s' % (
            bodyString,
            topic,
            future.result())
        )

    def save_json_data_to_gcs_object(
        self,
        bucketName,
        dirPath,
        prefix,
        data,
    ):
        """Save a JSON object to an object in GCS."""
        jsonString = json.dumps(data, sort_keys=True)
        objectName = self.save_json_string_to_gcs_object(
            bucketName,
            dirPath,
            prefix,
            jsonString,
        )
        return objectName

    def save_json_string_to_gcs_object(
        self,
        bucketName,
        dirPath,
        prefix,
        jsonString,
    ):
        """Save a JSON string to an object in GCS."""
        # create storage client
        storage_client = storage.Client()

        # set the bucket
        bucket = storage_client.bucket(bucketName)

        # generate the object name
        objectName = self.generate_json_object_name(dirPath, prefix)

        # create the blob
        blob = bucket.blob(objectName)

        # upload the blob
        blob.upload_from_string(
            jsonString,
            content_type='application/json'
        )

        return objectName


class Workday(object):
    """Workday Class."""

    def get_entry_orgunit_string(self, entry):
        """Return the orgunit string for the given Workday entry."""
        # define org unit fields from entry
        orgunit_fields = [
            'Dept_Hier_Lvl1_Name',
            'Dept_Hier_Lvl2_Name',
            'Dept_Hier_Lvl3_Name',
            'Dept_Hier_Lvl4_Name',
            'Dept_Hier_Lvl5_Name',
        ]

        # get orgunit segments from values
        orgunits = []
        for field in orgunit_fields:
            ou = entry.get(field)
            if ou and ou != 'The Broad Institute':
                orgunits.append(ou)

        # assemble orgunit string
        orgunit = ' > '.join(orgunits)

        return orgunit
