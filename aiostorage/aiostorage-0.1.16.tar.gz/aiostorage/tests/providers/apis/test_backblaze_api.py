import os

import pytest

from ....providers.backblaze import Backblaze

VIDEOS_PATH = os.path.join('aiostorage', 'tests', 'data', 'videos')
BUCKET_ID = os.environ['BACKBLAZE_TEST_BUCKET_ID']


@pytest.fixture
def storage():
    credentials = {
        'account_id': os.environ['BACKBLAZE_ACCOUNT_ID'],
        'app_key': os.environ['BACKBLAZE_APP_KEY'],
    }
    return Backblaze(**credentials)


@pytest.mark.asyncio
async def test_authenticate(storage):
    result = await storage.authorize()
    assert {'apiUrl', 'authorizationToken'}.issubset(result)


@pytest.mark.asyncio
async def test__get_upload_url(storage):
    result = await storage.authorize()
    assert {'apiUrl', 'authorizationToken'}.issubset(result)
    result = await storage._get_upload_url(BUCKET_ID)
    assert {'uploadUrl', 'authorizationToken'}.issubset(result)


@pytest.mark.parametrize(
    ('bucket_id', 'file_to_upload', 'content_type', 'expected'),
    (
        (BUCKET_ID,
         'Helene Fischer - Atemlos durch die Nacht.mp4', 'video/mp4', 1607175),
        (BUCKET_ID,
         'Luis Fonsi - Despacito ft Daddy Yankee.mp4', 'video/mp4', 3452397),
        (BUCKET_ID,
         'Rino Gaetano - Ma il cielo è sempre più blu.webm', 'video/webm',
         262276),
        (BUCKET_ID,
         'Stromae - Alors On Danse.webm', 'video/webm', 664295),
    )
)
@pytest.mark.asyncio
async def test_upload_file(storage, bucket_id, file_to_upload, content_type,
                           expected):
    result = await storage.authorize()
    assert {'apiUrl', 'authorizationToken'}.issubset(result)
    result = await storage.upload_file(bucket_id, os.path.join(
        VIDEOS_PATH, file_to_upload), content_type)
    assert result['contentLength'] == expected
