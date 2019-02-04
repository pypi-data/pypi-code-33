import warnings
import json
import time

import boto3
from botocore.client import ClientError

from d6tpipe.exceptions import ResourceExistsError

def create_bucket_with_users(session, remote_name, prefix='d6tpipe-', bucket_name=None, user_name=None, bucket_exists='keep-keep', user_exists='keep-keep'):
    """

    Create s3 bucket with correct users, credentials and policies for use with d6tpipe. It will create 2 users, one for read one for write

    Args:
        session (obj): boto3 session
        remote_name (str): name of pipe to name bucket and user
        prefix (str): prefix for naming bucket and user
        bucket_name (str): force name of bucket
        user_name (str): force name of user
        bucket_exists (str): control when bucket exists. 'raise', 'ignore', 'recreate', 'recreate-noconfirm', see notes
        user_exists (str): control when user exists. 'raise', 'use-new', 'use-keep' or 'recreate', see notes

    Returns:
        bool: success status

    Note:
        * bucket_exists:
            * 'raise': raise exception
            * 'keep-keep': keep existing bucket and policy
            * 'keep-new': keep existing bucket and but create new policy
            * 'recreate': delete existing bucket INCLUDING ALL CONTENT
            * 'recreate-noconfirm': like recreate but don't ask for confirmation to delete all
        * user_exists:
            * 'raise': raise exception
            * 'keep-keep': keep existing user and credentials
            * 'keep-new': keep existing user and but create new credentials
            * 'recreate': delete existing user and create new one with new credentials
            * 'recreate-noconfirm': like recreate but don't ask for confirmation to delete all
    """

    try:
        import tenacity
    except:
        raise ModuleNotFoundError('To use this function need an additional library, `pip install tenacity`')

    if bucket_name is None:
        bucket_name = prefix+remote_name
    if user_name is None:
        user_name = prefix+remote_name
    users = {'read':user_name+'-read','write':user_name+'-write'}
    usr_creds = dict([(k,{'AccessKey':{'AccessKeyId':None, 'SecretAccessKey':None}}) for k,u in users.items()])

    is_bucket_exists = True
    is_create_creds = True
    is_create_policy = True

    s3r = session.resource('s3')
    iam = session.client('iam')

    try:
        s3r.meta.client.head_bucket(Bucket=bucket_name)
    except ClientError:
        is_bucket_exists = False

    def _usr_exists(usr):
        try:
            iam.get_user(UserName=usr)
            return True
        except iam.exceptions.NoSuchEntityException:
            return False
    is_user_exists = any([_usr_exists(u) for u in users.values()])

    if is_bucket_exists:
        if bucket_exists=='raise':
            raise ResourceExistsError('bucket "{}" already exists'.format(bucket_name))
        elif 'recreate' in bucket_exists:
            delete_bucket(session, bucket_name, confirm='noconfirm' not in bucket_exists)
            is_bucket_exists = False
        elif 'keep' in bucket_exists:
            warnings.warn('bucket "{}" already exists, keeping bucket'.format(bucket_name))
            if bucket_exists == 'keep-keep':
                is_create_policy = False
        else:
            raise ValueError('invalid value for `bucket_exists`')

    if is_user_exists:
        if user_exists=='raise':
            raise ResourceExistsError('users {} already exists'.format(users.values()))
        elif 'recreate' in user_exists:
            [delete_user(session, u, confirm='noconfirm' not in user_exists) for u in users.values()]
            is_user_exists = False
        elif 'keep' in user_exists:
            warnings.warn('user {} already exists, keeping user'.format(users.values()))
            if user_exists == 'keep-keep':
                is_create_creds = False
                warnings.warn('keeping credentials for users {}, you will have to manually add them to the result'.format(users.values()))
            else:
                warnings.warn('creating new credentials for users {} '.format(users.values()))
        else:
            raise ValueError('invalid value for `user_exists`')

    # create bucket and user
    if not is_bucket_exists:
        s3r.create_bucket(Bucket=bucket_name)
    if not is_user_exists:
        [iam.create_user(UserName=u) for u in users.values()]
    if is_create_creds:
        usr_creds = dict([(k,iam.create_access_key(UserName=u)) for k,u in users.items()])

    # set policy
    _bucket_policy(session,bucket_name,users['read'],users['write'],is_create_policy)

    r = \
    {
        'name': remote_name,
        'location':bucket_name,
        'protocol':'s3',
        'readCredentials' : {
            'aws_access_key_id': usr_creds['read']['AccessKey']['AccessKeyId'],
            'aws_secret_access_key': usr_creds['read']['AccessKey']['SecretAccessKey']
        },
        'writeCredentials' : {
            'aws_access_key_id': usr_creds['write']['AccessKey']['AccessKeyId'],
            'aws_secret_access_key': usr_creds['write']['AccessKey']['SecretAccessKey']
        }
    }

    return r


def _bucket_policy(session, bucket_name, usr_read, usr_write, overwrite):
    try:
        import tenacity
    except:
        raise ModuleNotFoundError('To use this function need an additional library, `pip install tenacity`')

    s3r = session.resource('s3')
    iam = session.client('iam')

    if overwrite:
        bucket_policy = \
            {
                'Version': '2012-10-17',
                'Statement': [
                ]
            }
    else:
        r = s3r.meta.client.get_bucket_policy(Bucket=bucket_name)
        bucket_policy = json.loads(r['Policy'])

    usr_read_meta = iam.get_user(UserName=usr_read)
    d = {
        "Sid": "read",
        'Effect': 'Allow',
        'Principal': {"AWS": usr_read_meta['User']['Arn']},
        'Action': ['s3:GetObject', "s3:ListBucket"],
        'Resource': ["arn:aws:s3:::{}/*".format(bucket_name), "arn:aws:s3:::{}".format(bucket_name)]
    }
    bucket_policy['Statement'].append(d)

    usr_write_meta = iam.get_user(UserName=usr_write)
    d = {
        "Sid": "write",
        'Effect': 'Allow',
        'Principal': {"AWS": usr_write_meta['User']['Arn']},
        'Action': ['s3:PutObject', "s3:DeleteObject", "s3:ListBucket"],
        'Resource': ["arn:aws:s3:::{}/*".format(bucket_name), "arn:aws:s3:::{}".format(bucket_name)]
    }
    bucket_policy['Statement'].append(d)

    @tenacity.retry(wait=tenacity.wait_fixed(5), stop=tenacity.stop_after_attempt(5))
    def _put():
        try:
            r = s3r.meta.client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))
            return r
        except ClientError as e:
            if 'Invalid principal' in str(e):
                warnings.warn('waiting for aws to udpate')
                raise tenacity.TryAgain
            else:
                raise e

    r = _put()
    warnings.warn('waiting for aws to udpate')
    time.sleep(5)  # aws needs time to update
    return r


def delete_bucket(session, bucket_name, confirm=True):
    """

    Delete S3 bucket

    Args:
        session (obj): boto3 session
        bucket_name (str): name of bucket
        confirm (bool): ask to confirm delete

    Returns:
        bool: success status

    """

    if confirm:
        c = input('Confirm deleting bucket "{}" including all content (y/n)'.format(bucket_name))
        if c=='n': return None

    s3r = session.resource('s3')
    s3b = s3r.Bucket(bucket_name)

    for key in s3b.objects.all():
        key.delete()
    s3b.delete()

    return True


def delete_user(session, user_name, confirm=True):
    """

    Delete AWS user

    Args:
        session (obj): boto3 session
        user_name (str): name of user
        confirm (bool): ask to confirm delete

    Returns:
        bool: success status

    """

    if confirm:
        c = input('Confirm deleting user "{}" including all access keys (y/n)'.format(user_name))
        if c=='n': return None

    iam = session.client('iam')
    usr_meta = iam.get_user(UserName=user_name)
    for object in iam.list_access_keys(UserName=user_name)['AccessKeyMetadata']:
        iam.delete_access_key(UserName=user_name, AccessKeyId=object['AccessKeyId'])
    iam.delete_user(UserName=user_name)

    return True
