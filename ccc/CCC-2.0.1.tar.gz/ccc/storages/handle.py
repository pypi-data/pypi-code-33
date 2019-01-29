"""
Google cloud storage handle files - and file utilities
"""
from __future__ import print_function

import errno
import os
import tempfile
import uuid
from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from google.cloud import storage


def add_date_to_filename(file_name):
    """Append a date structure to the filename on gc"""
    current_date = datetime.utcnow().strftime("%Y/%m/%d/")
    return "{}{}".format(current_date, file_name)


def get_random_image_name(suffix):
    """return a unique name - uuid"""
    random_name = "{}{}".format(uuid.uuid4().hex, suffix)
    return add_date_to_filename(random_name)


def get_remote_path_from_url(blob_url):
    if settings.GS_MEDIA_BUCKET_NAME in blob_url:
        bucket_name = settings.GS_MEDIA_BUCKET_NAME
        return urlparse(blob_url).path.replace(bucket_name,"").replace('//',"")
    return


def get_blob_as_string(blob_name):
    """.."""
    storage_client = storage.Client()
    media_bucket = settings.GS_MEDIA_BUCKET_NAME
    # TODO use template cache.
    if media_bucket in blob_name:
        bucket = storage_client.get_bucket(media_bucket)
        blob = bucket.blob(get_remote_path_from_url(blob_name))
        blob_string = blob.download_as_string()
        return blob_string

    return


def download_remote_filename_to(file_url, origin_name, bucket_name=settings.GS_MEDIA_BUCKET_NAME):
    """Get remote file from google cloud storage"""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob(get_remote_path_from_url(file_url, bucket_name))

    if not os.path.exists(os.path.dirname(origin_name)):
        try:
            os.makedirs(os.path.dirname(origin_name))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    blob.download_to_filename(origin_name)

    return True


def store_file_media(source_file, destination='uploads/', public=True):
    """Upload a media file from a source file (memory) to MEDIA google cloud storage"""

    filename, file_extension = os.path.splitext(source_file.name)
    new_image_name = destination + get_random_image_name(file_extension)

    with tempfile.NamedTemporaryFile(mode='w+b', suffix=file_extension) as tmp_file:
        for chunk in source_file.chunks():
            tmp_file.write(chunk)

        storage_client = storage.Client()
        storage_bucket = storage_client.get_bucket(settings.GS_MEDIA_BUCKET_NAME)

        blob = storage_bucket.blob(new_image_name)
        blob.upload_from_filename(tmp_file.name)
        if public:
            blob.make_public()

        print('File {} uploaded to {}'.format(tmp_file.name, destination))

    return blob


def copy_file_media_from(source_file_name, to_destination_string):
    """Copy a file from one destination to another into MEDIA bucket, with a new name..."""
    media_bucket = settings.GS_MEDIA_BUCKET_NAME
    storage_client = storage.Client()
    source_bucket = storage_client.get_bucket(media_bucket)

    file_to_copy = source_bucket.blob(source_file_name)

    to_destination_string = "{}{}".format(to_destination_string, add_date_to_filename(source_file_name.split('/')[-1]))
    new_file = source_bucket.copy_blob(file_to_copy, source_bucket, to_destination_string)
    new_file.make_public()

    print('Blob {} in bucket {} copied to blob {} in bucket {}.'.format(
        file_to_copy.name, source_bucket.name, new_file.name, source_bucket.name))

    return new_file


def get_thumbnail(source_file, to_destination='thumbnails/'):
    """Sorl Wrappe. Get or generate a thumbnail integrated with google storage"""
    from PIL import ImageFile
    from sorl.thumbnail import get_thumbnail

    ImageFile.LOAD_TRUNCATED_IMAGES = True

    # get from cache or create... Cache can clear via django commans so is important persist thumbnails in bucket.
    cache_thumbnail = get_thumbnail(source_file, '300x200', quality=99)
    thumbnail = copy_file_media_from(cache_thumbnail.name, to_destination)

    return thumbnail


def get_name_from_blob(blob_url_string):
    """Return name from blob file stored on gcloud storage"""
    return blob_url_string.split('/')[-1]


def get_file_structure_from_blob(blob_url_string):
    """Return string with file structure from blob stored on gcloud storage"""
    #TODO
    path = blob_url_string.split('/')
    return "{}/{}/{}/".format(path[-2], path[-3], path[-4])
