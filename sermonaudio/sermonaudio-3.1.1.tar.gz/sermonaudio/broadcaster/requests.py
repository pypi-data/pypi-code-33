import datetime
import functools
from http import HTTPStatus

from typing import Optional, List

from sermonaudio import API, APIException, _session
from sermonaudio.models import Sermon, SermonEventType
from sermonaudio.utils import update_kwargs_for_key, join_url_path


class BroadcasterAPIError(APIException):  # pragma: no cover
    pass


def parse_sermon(response) -> Sermon:  # pragma: no cover
    if response.ok:
        return Sermon.parse(response.json())
    else:
        raise BroadcasterAPIError(response.json())


def check_response_code_or_throw(response) -> bool:  # pragma: no cover
    """Returns true if response is successful from an endpoint that returns nothing."""
    if response.ok:
        return True
    else:
        if response.json():
            raise BroadcasterAPIError(response.json())
        else:
            # If no error message was returned, use the status code.
            raise BroadcasterAPIError({'errors': {'status_code': response.status_code}})


class Broadcaster(API):  # pragma: no cover. Unfortunately we can't test this w/o a test account...
    @classmethod
    def create_or_update_sermon(
        cls,
        sermon_id: Optional[str],
        accept_copyright: bool,
        full_title: str,
        speaker_name: str,
        preach_date: datetime.date,
        publish_timestamp: Optional[datetime.datetime],
        event_type: SermonEventType,
        display_title: Optional[str],
        subtitle: Optional[str],
        bible_text: Optional[str],  # TODO: structure this data
        more_info_text: Optional[str],
        language_code: str,
        keywords: Optional[List[str]],
        **kwargs,
    ) -> Sermon:
        """Creates a new sermon record or updates an existing one (media uploaded separately).

        :param sermon_id: The sermon ID, if you are updating an existing sermon. Otherwise, None.
        :param accept_copyright: A boolean value indicating that you agree that you are allowed to upload this content.
        :param full_title: The full sermon title.
        :param speaker_name: The speaker name (please be consistent; speakers will be created if they don't exist).
        :param preach_date: The date the sermon was preached.
        :param publish_timestamp: The time that the sermon should be visible on the site. You must submit this in order
        for the sermon to be visible to the public. Callers are encouraged to use timezone aware objects to ensure
        that the correct timestamp is generated.
        :param event_type: The type of event that this sermon was preached at.
        :param display_title: An alternate, shorter version of the title to be displayed in ID3v1 tags and parts of
        the legacy site (30 char limit)
        :param subtitle: The subtitle of the sermon (or the series, if multiple sermons use the same subtitle; this
        will likely be reworked in the future)
        :param bible_text: The scripture passage(s) that this sermon was derived from
        :param more_info_text: Additional info about the sermon that you wish to share
        :param language_code: The ISO 639 language code for the sermon.
        :param keywords: A list of keywords for this sermon.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: The created sermon
        """
        update_kwargs_for_key(
            kwargs,
            'params',
            {
                'acceptCopyright': accept_copyright,
                'fullTitle': full_title,
                'speakerName': speaker_name,
                'preachDate': preach_date.isoformat(),
                'publishTimestamp': int(publish_timestamp.timestamp()) if publish_timestamp else None,
                'eventType': event_type.value,
                'displayTitle': display_title,
                'subtitle': subtitle,
                'bibleText': bible_text,
                'moreInfoText': more_info_text,
                'languageCode': language_code,
                'keywords': ' '.join(keywords) if keywords else None,
            },
        )

        if sermon_id:
            path = join_url_path('node', 'sermons', sermon_id)
            method = 'put'
        else:
            path = join_url_path('node', 'sermons')
            method = 'post'

        return cls._request(path, method, parse_func=parse_sermon, **kwargs)

    @classmethod
    def publish_sermon(cls, sermon_id: str):  # pragma: no cover
        path = join_url_path('node', 'sermons', sermon_id)
        params = {'publishNow': True}
        return cls.patch(path, params)

    @classmethod
    def delete_sermon(cls, sermon_id: str):  # pragma: no cover
        path = join_url_path('node', 'sermons', sermon_id)
        return cls.delete(path)

    @classmethod
    def duplicate_sermon(cls, sermon_id: str, **kwargs) -> Sermon:  # pragma: no cover
        path = join_url_path('node', 'sermons', sermon_id, 'duplicate')
        return cls.post(path, parse_func=parse_sermon, **kwargs)

    @classmethod
    def _upload_media(cls, upload_type: str, sermon_id: str, path: str, **kwargs):  # pragma: no cover
        """Uploads media for a sermon.
        :param upload_type: The type of media to upload.
        :param sermon_id: The Sermon ID you are uploading media for.
        :param path: The path to the file on disk.
        :param kwargs: Additional arguments to pass to the underlying post method.
        :return: No return value. Throws a BroadcasterAPIError with details on failure.
        """
        update_kwargs_for_key(kwargs, 'params', {'uploadType': upload_type, 'sermonID': sermon_id})

        response = cls.post('media', **kwargs)

        if response.status_code != HTTPStatus.CREATED:
            raise BroadcasterAPIError({'error': 'Unable to create media upload', 'json': response.json()})

        upload_url = response.json()['uploadURL']

        with open(path, 'rb') as fp:
            response = _session.post(upload_url, data=fp, stream=True)
            if not response.ok:
                raise BroadcasterAPIError(
                    {
                        'error': f'Received unexpected HTTP status code {response.status_code} when uploading data.',
                        'response': response.content,
                    }
                )

    upload_audio = functools.partialmethod(_upload_media, 'original-audio')
    upload_video = functools.partialmethod(_upload_media, 'original-video')

    #
    # Series
    #
    @classmethod
    def create_series(cls, new_title: str, broadcaster_id: str) -> bool:  # pragma: no cover
        """Creates an empty series.

        The new series can't already exist.

        :param new_title: The new title for the series.
        :return: Boolean indicating success.
        """
        path = join_url_path('node', 'broadcasters', broadcaster_id, 'series')
        return cls.post(path, data={'series_name': new_title}, parse_func=lambda res: check_response_code_or_throw(res))

    @classmethod
    def rename_series(cls, current_title: str, new_title: str, broadcaster_id) -> bool:  # pragma: no cover
        """Renames a series.

        If the new series name already exists, all sermons from the
        original series will be merged in.

        :param current_title: The current title of the series.
        :param new_title: The new title for the series.
        :return: Boolean indicating success.
        """
        path = join_url_path('node', 'broadcasters', broadcaster_id, 'series', current_title)
        return cls.patch(
            path, data={'new_series_name': new_title}, parse_func=lambda res: check_response_code_or_throw(res)
        )

    @classmethod
    def delete_series(cls, title: str, broadcaster_id: str) -> bool:  # pragma: no cover
        """Deletes a series.

        Deleting a series does not delete the sermons in the series.

        :param title: The series to delete.
        :return:  Boolean indicating success.
        """
        path = join_url_path('node', 'broadcasters', broadcaster_id, 'series', title)
        return cls.delete(path, parse_func=lambda res: check_response_code_or_throw(res))
