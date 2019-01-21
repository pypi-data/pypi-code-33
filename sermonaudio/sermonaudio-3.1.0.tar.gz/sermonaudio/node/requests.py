import functools

from typing import List, Optional

from requests import Response

from sermonaudio import API, APIException, models
from sermonaudio.utils import update_kwargs_for_key, join_url_path

URL_PATH = 'node'


class NodeAPIError(APIException):
    pass


def parse_node(response) -> models.Node:
    if response.ok:
        return models.Node.parse(response.json())
    else:
        raise NodeAPIError(response.json())


class Node(API):
    """An interface to the SermonAudio.com node API v2.

    This class provides a variety of low-level and high-level helpers to make it
    easy to interact with the API. A number of higher-level helpers are exposed to
    make common API calls easy. However, the API has many options, and we do not
    necessarily comprehensively model them all here. Please refer to the documentation,
    and if you need to build additional methods for your application, you may use the lower
    level helpers at the top of the class to build your own `Node` subclass with additional
    high-level helper methods.
    """

    #
    # Low-level building blocks
    #

    get_node = functools.partialmethod(API.get, parse_func=parse_node)
    get_sermon_list_node = functools.partialmethod(
        get_node, parse_func=lambda res: [models.Sermon.parse(rec) for rec in parse_node(res).results]
    )

    class PaginatedResponse:
        def __init__(self, page: int, page_size: int, response: models.Node, result_processing_func=None):
            self.page = page
            self.page_size = page_size
            self.next_url = response.next
            self.total_count = response.total_count
            self.results = (
                [result_processing_func(result) for result in response.results]
                if result_processing_func
                else response.results
            )

    #
    # Sermons
    #

    @classmethod
    def get_sermons(
        cls,
        path: str = None,
        page: int = 1,
        page_size: Optional[int] = None,
        book: Optional[models.OSISBook] = None,
        chapter: Optional[int] = None,
        chapter_end: Optional[int] = None,
        verse: Optional[int] = None,
        verse_end: Optional[int] = None,
        event_type: Optional[models.SermonEventType] = None,
        search_keyword: Optional[str] = None,
        language_code: Optional[str] = None,
        require_audio: bool = False,
        require_video: bool = False,
        series: Optional[str] = None,
        broadcaster_id: str = None,
        sermon_ids: [str] = None,
        speaker_name: str = None,
        year: Optional[int] = None,
        sort_by: Optional[models.SermonSortOption] = None,
        include_drafts: bool = False,
        include_scheduled: bool = False,
        include_published: bool = True,
        **kwargs,
    ) -> PaginatedResponse:
        """Returns a set of sermons with pagination data, when available.

        :param path: The path to the endpoint you want to call (defaults to the all-purpose sermon node endpoint).
        :param page: The page number to load (defaults to 1).
        :param page_size: The number of items per page (currently defaults to 50 if omitted).
        :param kwargs: Additional arguments to pass to the underlying get method.
        :param book: The book of the Bible to limit results to.
        :param chapter: The chapter of the book to limit results to.
        :param chapter_end: If you want to query a range of chapters, the range will span from chapter to chapter_end.
        :param verse: The verse of the chapter to limit results to.
        :param verse_end: If you want to query a range of verses, the range will span from verse to verse_end.
        :param event_type: The type of event to limit results to, if any.
        :param search_keyword: Keywords to search by.
        :param language_code: The language code to limit results to.
        :param require_audio: If true, all results will have ready-to-play audio.
        :param require_video: If true, all results will have ready-to-play video.
        :param series: The series to limit results to.
        :param broadcaster_id: The ID of the broadcaster to limit results to.
        :param speaker_name: The speaker name to limit results to.
        :param year: The year to limit results to (preach date, not upload date).
        :param sort_by: A sort to apply to the results. Defaults to preach date descending.
        :param include_drafts: If true, include sermons with no publish date.
        :param include_scheduled: If true, include sermons set to be published in the future.
        :param include_published: If true, include published sermons.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A sermon list response with pagination data, if available.
        """
        path = path or join_url_path(URL_PATH, 'sermons')
        update_kwargs_for_key(
            kwargs,
            'params',
            {
                'page': page,
                'pageSize': page_size,
                'book': book.value if book else None,
                'chapter': chapter,
                'chapterEnd': chapter_end,
                'verse': verse,
                'verseEnd': verse_end,
                'eventType': event_type.value if event_type else None,
                'searchKeyword': search_keyword,
                'languageCode': language_code,
                'requireAudio': require_audio,
                'requireVideo': require_video,
                'series': series,
                'broadcasterID': broadcaster_id,
                'sermonIDs': ','.join(sermon_ids) if sermon_ids else None,
                'speakerName': speaker_name,
                'year': year,
                'sortBy': sort_by.value if sort_by else None,
                'includeDrafts': include_drafts,
                'includeScheduled': include_scheduled,
                'includePublished': include_published,
            },
        )

        return cls.get_node(
            path,
            parse_func=lambda res: cls.PaginatedResponse(page, page_size, parse_node(res), models.Sermon.parse),
            **kwargs,
        )

    @classmethod
    def get_sermon(cls, sermon_id: str, **kwargs) -> Optional[models.Sermon]:
        """Fetches info for a single sermon, if it exists.

        :param sermon_id: The ID of the sermon you want to fetch.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: models.Sermon or None
        """
        return cls.get(
            join_url_path(URL_PATH, 'sermons', str(sermon_id)),
            parse_func=lambda res: models.Sermon.parse(res.json()) if res.ok else None,
            **kwargs,
        )

    @classmethod
    def delete_media(cls, sermon_id: str, media_type: models.MediaClass, **kwargs) -> Response:  # pragma: no cover
        """Deletes media of a given type for a single sermon.

        :param sermon_id: The ID of the sermon whose media you want to delete.
        :param media_type: The type of media you want to delete.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: bool indicating success or failure
        """
        params = {'sermonID': sermon_id, 'target': media_type.value}
        return cls.post(join_url_path('jobs', 'delete'), params=params, **kwargs)

    #
    # Broadcasters
    #

    @classmethod
    def get_broadcaster(cls, broadcaster_id: str, **kwargs) -> Optional[models.Broadcaster]:
        """Fetches info for a single broadcaster, if it exists.

        :param broadcaster_id: The ID of the broadcaster you want to fetch.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: models.Broadcaster or None
        """
        return cls.get(
            join_url_path(URL_PATH, 'broadcasters', str(broadcaster_id)),
            parse_func=lambda res: models.Broadcaster.parse(res.json()) if res.ok else None,
            **kwargs,
        )

    @classmethod
    def get_broadcasters_near_location(
        cls, latitude: float, longitude: float, meters: int, **kwargs
    ) -> List[models.RelativeBroadcasterLocation]:
        """Fetches a list of broadcasters near a location.

        :param latitude: The latitude of the search origin.
        :param longitude: The longitude of the search origin.
        :param meters: The distance from the origin to search.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A list of broadcaster relative location objects
        """
        update_kwargs_for_key(kwargs, 'params', {'latitude': latitude, 'longitude': longitude, 'meters': meters})
        return cls.get(
            join_url_path(URL_PATH, 'broadcasters', 'near_location'),
            parse_func=lambda res: [models.RelativeBroadcasterLocation.parse(rec) for rec in parse_node(res).results],
            **kwargs,
        )

    @classmethod
    def get_sermon_event_types(cls, broadcaster_id: str = None, **kwargs) -> List[models.SermonEventTypeDetail]:
        """Fetches a list of valid sermon event types for a broadcaster.

        :param broadcaster_id: You can omit this if you are using a broadcaster API key.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A list of sermon event type detail objects
        """
        update_kwargs_for_key(kwargs, 'params', {'broadcaster_id': broadcaster_id})
        return cls.get(
            join_url_path(URL_PATH, 'filter_options', 'sermon_event_types'),
            parse_func=lambda res: [models.SermonEventTypeDetail.parse(rec) for rec in parse_node(res).results],
            **kwargs,
        )

    #
    # Series
    #

    @classmethod
    def get_series_list(
        cls,
        broadcaster_id: str = None,
        page: int = 1,
        page_size: Optional[int] = None,
        sort_by: models.SeriesSortOrder = models.SeriesSortOrder.LAST_UPDATED,
        **kwargs,
    ) -> PaginatedResponse:
        """Fetches a sermon series list for a broadcaster.

        :param broadcaster_id: You can omit this if you are using a broadcaster API key.
        :param page: The page number to load (defaults to 1).
        :param page_size: The number of items per page (currently defaults to 50 if omitted).
        :param sort_by: A sort to apply to the results. Defaults to last updated.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A paginated response, with the results being SermonSeries objects.
        """
        update_kwargs_for_key(kwargs, 'params', {'page': page, 'pageSize': page_size, 'sort_by': sort_by.value})

        path = join_url_path(URL_PATH, 'broadcasters', broadcaster_id, 'series')
        return cls.get_node(
            path,
            parse_func=lambda res: cls.PaginatedResponse(page, page_size, parse_node(res), models.SermonSeries.parse),
            **kwargs,
        )

    @classmethod
    def get_series(cls, series_name: str, broadcaster_id: str = None, **kwargs) -> Optional[models.SermonSeries]:
        """Fetches a single series.

        :param series_name: The name of the series.
        :param broadcaster_id: You can omit this if you are using a broadcaster API key.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A single models.SermonSeries object, or None if series name does not exist.
        """
        return cls.get(
            join_url_path(URL_PATH, 'broadcasters', broadcaster_id, 'series', series_name),
            parse_func=lambda res: models.SermonSeries.parse(res.json()) if res.ok else None,
            **kwargs,
        )

    #
    # Misc
    #

    @classmethod
    def get_speaker(cls, speaker_name: str, **kwargs) -> Optional[models.Speaker]:
        """Fetches a single speaker.

        :param speaker_name: The name of the speaker (exactly as it appears on the SA site).
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A single models.Speaker object, or None if speaker does not exist.
        """
        return cls.get(
            join_url_path(URL_PATH, 'speakers', speaker_name),
            parse_func=lambda res: models.Speaker.parse(res.json()) if res.ok else None,
            **kwargs,
        )

    @classmethod
    def get_speakers(
        cls, broadcaster_id: Optional[str] = None, query: Optional[str] = None, page_size: Optional[int] = 25, **kwargs
    ) -> List[models.Speaker]:
        """Fetches a list of speakers.

        :param broadcaster_id: The ID of the broadcaster the speakers must have preached at.
        :param query: A search query to try to locate the speaker by.
        :param page_size: The number of results to return.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A list of models.Speaker objects
        """
        update_kwargs_for_key(
            kwargs, 'params', {'broadcasterID': broadcaster_id, 'query': query, 'pageSize': page_size}
        )
        return cls.get(
            join_url_path(URL_PATH, 'speakers'),
            parse_func=lambda res: [models.Speaker.parse(rec) for rec in parse_node(res).results],
            **kwargs,
        )

    @classmethod
    def get_webcasts_in_progress(cls, broadcaster_id: str = None, **kwargs) -> List[models.Webcast]:
        """Fetches a list of webcasts that are currently in progress.

        :param broadcaster_id: You can omit this if you are using a broadcaster API key.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A list of webcasts that are live now
        """
        update_kwargs_for_key(kwargs, 'params', {'broadcasterID': broadcaster_id})
        return cls.get(
            join_url_path(URL_PATH, 'webcasts'),
            parse_func=lambda res: [models.Webcast.parse(rec) for rec in parse_node(res).results],
            **kwargs,
        )

    @classmethod
    def get_spurgeon_devotional(
        cls, kind: models.SpurgeonDevotionalType, month: int, day_of_month: int, **kwargs
    ) -> Optional[models.SpurgeonDevotional]:
        """Returns the Spurgeon devotional for a given month and day

        :param kind: The kind of devotional (one of the values in models.SpurgeonDevotionalType).
        :param month: The month component of the date.
        :param day_of_month: The day of month component of the date.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A devotional object or None
        """
        update_kwargs_for_key(kwargs, 'params', {'type': kind.value, 'month': month, 'day_of_month': day_of_month})

        def parse_spurgeon(result):
            data = parse_node(result).results

            return models.SpurgeonDevotional.parse(data) if data else None

        return cls.get(join_url_path(URL_PATH, 'spurgeon_devotional'), parse_func=parse_spurgeon, **kwargs)

    @classmethod
    def get_filter_options(cls, broadcaster_id: str, **kwargs) -> Optional[models.FilterOptions]:
        """Returns filter options for the given broadcaster

        :param broadcaster_id: The broadcaster ID you are interested in.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A filter options object containing available filters for the broadcaster or None
        """
        return cls.get(
            join_url_path(URL_PATH, 'broadcasters', broadcaster_id, 'filter_options'),
            parse_func=lambda res: models.FilterOptions.parse(res.json()) if res.ok else None,
            **kwargs,
        )

    @classmethod
    def get_all_languages(cls, **kwargs) -> List[models.Language]:
        """Returns a list of all supported sermon languages

        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: [models.Language]
        """
        return cls.get(
            join_url_path(URL_PATH, 'filter_options', 'languages'),
            parse_func=lambda res: [models.Language.parse(rec) for rec in parse_node(res).results],
            **kwargs,
        )

    @classmethod
    def get_all_sermon_event_types(cls, **kwargs) -> List[models.Language]:
        """Returns a list of all supported sermon event types

        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: [models.Language]
        """
        return cls.get(
            join_url_path(URL_PATH, 'filter_options', 'sermon_event_types'),
            parse_func=lambda res: [models.SermonEventTypeDetail.parse(rec) for rec in parse_node(res).results],
            **kwargs,
        )

    @classmethod
    def get_speakers_for_broadcaster(cls, broadcaster_id: str = None, **kwargs) -> List[models.Speaker]:
        """Fetches a list of all speakers for a broadcaster.

        In contrast to get_speakers(), which searches across multiple
        broadcasters, this returns a list of all speakers associated
        with the given broadcaster.

        :param broadcaster_id: The ID of the broadcaster.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A list of models.Speaker objects.
        """
        update_kwargs_for_key(kwargs, 'params', {'broadcasterID': broadcaster_id})
        return cls.get(
            join_url_path(URL_PATH, 'broadcasters', broadcaster_id, 'speakers'),
            parse_func=lambda res: [models.Speaker.parse(rec) for rec in parse_node(res).results],
            **kwargs,
        )

    @classmethod
    def get_speakers_for_series(cls, broadcaster_id: str, series_name: str, **kwargs) -> List[models.Speaker]:
        """Fetches a list of all speakers for a broadcaster's series.

        :param broadcaster_id: The ID of the broadcaster.
        :param series_name: The name of the series.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A list of models.Speaker objects.
        """
        return cls.get(
            join_url_path(URL_PATH, 'broadcasters', broadcaster_id, 'series', series_name, 'speakers'),
            parse_func=lambda res: [models.Speaker.parse(rec) for rec in parse_node(res).results],
            **kwargs,
        )

    @classmethod
    def get_speaker_sermon_counts_for_broadcaster(
        cls, broadcaster_id: str = None, **kwargs
    ) -> List[models.SermonCountForSpeaker]:
        """Fetches a list of sermon counts for each speaker for a broadcaster.

        This method returns a list of all speakers for a specified
        broadcaster and the number of sermons preached for that
        broadcaster only. This restricted count is useful for ranking
        speakers by the number of sermons they've preached for a
        specific broadcaster. The total number of sermons preached by a
        speaker can be high for some guest speakers, but these speakers
        may have preached only few sermons for any given broadcaster.

        :param broadcaster_id: The ID of the broadcaster.
        :param kwargs: Additional arguments to pass to the underlying get method.
        :return: A list of models.SpeakerSermonCount objects.
        """
        update_kwargs_for_key(kwargs, 'params', {'broadcasterID': broadcaster_id})
        return cls.get(
            join_url_path(URL_PATH, 'broadcasters', broadcaster_id, 'speakers', 'sermon_counts'),
            parse_func=lambda res: [models.SermonCountForSpeaker.parse(rec) for rec in parse_node(res).results],
            **kwargs,
        )
