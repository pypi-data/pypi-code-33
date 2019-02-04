import magic
import requests
import json
from pathlib import Path
import shutil

class ModerageClient():

    def __init__(self, host='http://localhost', port='8118', cache_location=None):

        self._host = host
        self._port = port

        self._root_url = '%s:%s/v0/experiment' % (host, port)

        if not cache_location:
            self._cache_location = Path.home().joinpath('.moderage')
            if not self._cache_location.exists():
                self._cache_location.mkdir()


    def save(self, meta_category, meta, files):
        """

        :param meta_category: A category name for this experiment, or this dataset
        :param meta: meta information for this experiment or dataset
        :param files: A list of files and metadata associated with this experiment or dataset

        Files must be in the following format:

        [
            "filename": "./path/to/my/file.xyz",
            "caption": "This is a description of my file"
        ]

        :return:
        """

        create_payload = {
            'metaCategory': meta_category,
            'meta': meta,
        }

        file_info_payload = {
            'files': [self._process_file_info(f) for f in files]
        }

        multipart_payload = [('files', (f['filename'],open(f['filename'], 'rb'))) for f in files]

        multipart_payload.append(('file_metadata', (None, json.dumps(file_info_payload))))

        create_response = requests.post('%s/create' % self._root_url, json=create_payload)

        assert create_response.status_code == 201, create_response.json()

        experiment = create_response.json()
        id = experiment['id']

        upload_response = requests.post('%s/%s/%s/uploadFiles' % (self._root_url, meta_category, id), files=multipart_payload)

        assert upload_response.status_code == 200, upload_response.json()

        return upload_response.json()


    def load(self, id, meta_category):

        get_response = requests.get('%s/%s/%s' % (self._root_url, meta_category, id))
        assert get_response.status_code == 200, get_response.json()
        experiment = get_response.json()

        # download the files from their uris
        for file_info in experiment['files']:

            cached_filename = self._cache_location.joinpath(meta_category, id, file_info['id'])

            # If we have not cached the file already, download it and move it to the cache directory
            if not cached_filename.exists():
                loaded_file = self._download_file(file_info)
                shutil.move(loaded_file, cached_filename)

            file_info['file'] = open(str(cached_filename), 'rb')

        return experiment



    def _download_file(self, file_info):
        if file_info['location'].startswith('http'):
            # Download the file
            requests.get(file_info['location'])

        elif file_info['location'].startswith('s3'):
            import boto3
            import botocore
            # Download the file
            s3 = boto3.resource('s3')

            bucket = file_info['bucket']
            key = file_info['key']

            try:
                s3.Bucket(bucket).download_file(key, file_info['filename'])
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist.")
                else:
                    raise

            loaded_file = ''

        else:

            loaded_file = file_info['location']
        return loaded_file

    def _process_file_info(self, file):
        """
        Get the mime type of the file
        :param file:
        :return:
        """
        file['contentType'] = magic.from_file(file['filename'], True)

        return file