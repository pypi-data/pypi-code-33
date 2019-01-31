"""Google Cloud Functions helper classes."""

import base64
import datetime
import json
# import logging

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

    def get_gcs_object_as_json(self, bucketname, filename):
        """Return the media from a gcs object as JSON."""
        # get file as a string
        filestring = self.get_gcs_object_as_string(bucketname, filename)

        # convert string to json
        print('Converting %s to JSON...' % (filename))
        json_data = json.loads(filestring)
        print('Successfully converted %s to JSON.' % (filename))

        return json_data

    def get_gcs_object_as_string(self, bucketname, filename):
        """Return the media from a gcs object as a string."""
        # create storage client
        storage_client = storage.Client()

        # set the bucket
        bucket = storage_client.bucket(bucketname)

        # create the blob
        blob = bucket.blob(filename)

        # download the blob
        path = 'gs://%s/%s...' % (bucketname, filename)
        print('Downloading %s as string...' % (path))
        filestring = blob.download_as_string()
        print('Successfully downloaded %s as string.' % (path))

        return filestring

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
        bodystring,
    ):
        """Send a PubSub notifiction to a specific project/topic."""
        # format the message data
        data = (u'%s' % (bodystring)).encode('utf-8')

        # create publisher
        publisher = pubsub_v1.PublisherClient()

        # create topic path
        topic_path = publisher.topic_path(project, topic)

        # create a future to publish the message
        future = publisher.publish(topic_path, data=data)

        # log the message
        print('Published to %s as message %s' % (
            # bodyString,
            topic,
            future.result())
        )

    def save_json_data_to_gcs_object(
        self,
        bucketname,
        dirPath,
        prefix,
        data,
    ):
        """Save a JSON object to an object in GCS."""
        print('Converting %s/%s JSON to string...' % (dirPath, prefix))
        jsonString = json.dumps(data, sort_keys=True)
        print('Successfully converted %s/%s JSON to string.' % (dirPath, prefix))

        objectName = self.save_json_string_to_gcs_object(
            bucketname,
            dirPath,
            prefix,
            jsonString,
        )
        return objectName

    def save_json_string_to_gcs_object(
        self,
        bucketname,
        dirPath,
        prefix,
        jsonstring,
    ):
        """Save a JSON string to an object in GCS."""
        # create storage client
        storage_client = storage.Client()

        # set the bucket
        bucket = storage_client.bucket(bucketname)

        # generate the object name
        objectName = self.generate_json_object_name(dirPath, prefix)

        # create the blob
        blob = bucket.blob(objectName)

        # upload the blob
        print('Uploading %s from string...' % (objectName))
        blob.upload_from_string(jsonstring, content_type='application/json')
        print('Successfully uploaded %s from string.' % (objectName))

        return objectName


class Workday(object):
    """Workday Class."""

    def get_entry_org_units(self, entry):
        """Return the orgunit string for the given Workday entry."""
        # define org unit fields from entry
        org_unit_fields = [
            'Dept_Hier_Lvl1_Name',
            'Dept_Hier_Lvl2_Name',
            'Dept_Hier_Lvl3_Name',
            'Dept_Hier_Lvl4_Name',
            'Dept_Hier_Lvl5_Name',
        ]

        # get a list of all non-empty orgunits
        org_units = []
        for field in org_unit_fields:
            ou = entry.get(field)
            if not ou:
                continue
            org_units.append(ou)

        return org_units

    def get_entry_org_unit_string(self, entry):
        """Return the orgunit string for the given Workday entry."""
        # get orgunit segments from values
        org_units_list = self.get_entry_org_units(entry)

        org_units = []
        for ou in org_units_list:
            if ou == 'The Broad Institute':
                continue
            org_units.append(ou)

        # assemble orgunit string
        org_unit = ' > '.join(org_units)

        return org_unit
