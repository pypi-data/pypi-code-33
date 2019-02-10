import asynctest
import pytest

from .. import (BlobStorage, BlobStorageMissingCredentialsError,
                BlobStorageUnrecognizedProviderError, )
from ..providers import backblaze, exceptions, PROVIDERS


@pytest.fixture
def storage():
    provider = 'backblaze'
    credentials = {
        'account_id': '23424',
        'app_key': 'sdfsdfs',
    }
    return BlobStorage(provider, **credentials)


def test_instance(storage):
    assert storage.provider


def test_unrecognized_provider():
    provider = 'fake'
    credentials = {
        'account_id': '23423',
        'app_key': 'sdfsdf',
    }
    with pytest.raises(BlobStorageUnrecognizedProviderError) as err:
        BlobStorage(provider, **credentials)
    assert ('Unrecognized object storage provider. Please select one of'
            f' {", ".join(PROVIDERS)}') == str(err.value)


def test_missing_credentials():
    provider = 'backblaze'
    credentials = {
        'accountId': '23423',
        'appKey': 'sdfsdf',
    }
    with pytest.raises(BlobStorageMissingCredentialsError) as err:
        BlobStorage(provider, **credentials)
    assert('Missing credentials for object storage provider authorization'
           == str(err.value))


def fake_provider_authorize_side_effect():
    return {'token': '23490xnzz3dfsejisdfa'}


def fake_provider_upload_file_side_effect(bucket_id, file_to_upload,
                                          content_type):
    return {'fileUploaded': file_to_upload, 'fileId': 234234,
            'fileBucketId': bucket_id, 'fileContentType': content_type}


@pytest.fixture
def mock_provider_authorize(monkeypatch):
    fake_provider_authorize = asynctest.CoroutineMock(
        backblaze.Backblaze.authorize,
        side_effect=fake_provider_authorize_side_effect
    )
    monkeypatch.setattr(
        backblaze.Backblaze, 'authorize', fake_provider_authorize)
    return fake_provider_authorize


@pytest.fixture
def mock_provider_upload_file(monkeypatch):
    fake_provider_upload_file = asynctest.CoroutineMock(
        backblaze.Backblaze.upload_file,
        side_effect=fake_provider_upload_file_side_effect)
    monkeypatch.setattr(
        backblaze.Backblaze, 'upload_file', fake_provider_upload_file)
    return fake_provider_upload_file


@pytest.mark.asyncio
async def test_upload_file(storage, mock_provider_authorize,
                           mock_provider_upload_file):
    bucket_id = '3432'
    file_to_upload = {'content_type': 'video/mp4', 'path': 'hello.mp4'}
    fake_result = {
        'fileUploaded': file_to_upload['path'],
        'fileId': 234234,
        'fileBucketId': bucket_id,
        'fileContentType': file_to_upload['content_type']
    }
    assert fake_result == await storage.upload_file(bucket_id, file_to_upload)


def fake_provider_authorize_error_side_effect():
    return {}


@pytest.fixture
def mock_provider_authorize_error(monkeypatch):
    fake_provider_authorize_error = asynctest.CoroutineMock(
        backblaze.Backblaze.authorize,
        side_effect=fake_provider_authorize_error_side_effect
    )
    monkeypatch.setattr(
        backblaze.Backblaze, 'authorize', fake_provider_authorize_error)
    return fake_provider_authorize_error


@pytest.mark.asyncio
async def test_upload_file_authorization_error(
    storage,
    mock_provider_authorize_error
):
    bucket_id = '3432'
    file_to_upload = {'content_type': 'video/mp4', 'path': 'hello.mp4'}
    with pytest.raises(exceptions.ProviderAuthorizationError):
        await storage.upload_file(bucket_id, file_to_upload)


def fake_provider_upload_file_error_side_effect(bucket_id, file_to_upload,
                                                content_type):
    return {}


@pytest.fixture
def mock_provider_upload_file_error(monkeypatch):
    fake_provider_upload_file_error = asynctest.CoroutineMock(
        backblaze.Backblaze.upload_file,
        side_effect=fake_provider_upload_file_error_side_effect
    )
    monkeypatch.setattr(
        backblaze.Backblaze, 'upload_file', fake_provider_upload_file_error)
    return fake_provider_upload_file_error


@pytest.mark.asyncio
async def test_upload_file_upload_file_error(
    storage,
    mock_provider_upload_file_error,
    mock_provider_authorize
):
    bucket_id = '3432'
    file_to_upload = {'content_type': 'video/mp4', 'path': 'hello.mp4'}
    with pytest.raises(exceptions.ProviderFileUploadError):
        await storage.upload_file(bucket_id, file_to_upload)
