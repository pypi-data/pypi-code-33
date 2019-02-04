from typing import Any
from typing import Dict
from typing import List

import boto3


def s3_bucket(bucket: str) -> Any:
    s3_resource = boto3.resource('s3')
    return s3_resource.Bucket(name=bucket)


def get_object(bucket_name: str, key: str, stream: bool = False) -> Any:
    bucket = s3_bucket(bucket_name)
    obj = bucket.Object(key=key)
    body = obj.get().get('Body')
    return body.iter_lines() if stream else body.read()


def put_object(bucket_name: str, key: str, content: str):
    bucket = s3_bucket(bucket_name)
    obj = bucket.Object(key=key)
    obj.put(Body=content, ContentType='application/json')


def delete_object(bucket_name: str, key: str):
    bucket = s3_bucket(bucket_name)
    obj = bucket.Object(key=key)
    obj.delete()


def list_objects(bucket_name: str, path: str = None) -> List[Any]:
    bucket = s3_bucket(bucket_name)
    return [obj.key for obj in bucket.objects.filter(
        Prefix=path if path else ''
    )]


def copy_objects(source_bucket_name: str, destination_bucket_name: str, keys: Dict[str, str],
                 destination_path: str = ''):
    destination_bucket = s3_bucket(destination_bucket_name)

    # Ensure folder structure of destination path
    if destination_path and not destination_path.endswith('/'):
        destination_path += '/'

    for source_key, destination_key in keys.items():
        copy_source = {
            'Bucket': source_bucket_name,
            'Key': source_key
        }
        obj = destination_bucket.Object(key=f'{destination_path}{destination_key}')
        obj.copy(copy_source)
