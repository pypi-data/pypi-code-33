"""API data structures"""
import datetime
import enum
import pytz

_model_override = {}

_generic_speaker_names = {'Various Speakers', 'Unknown Speaker'}


class MultipleOverrideError(Exception):
    pass


class Model:
    """Base model class.

    This is responsible for some of the magic surrounding model overrides. You really should
    inherit from this.
    """

    def __init__(self, obj: dict):
        super().__init__()

        self.__obj = obj

    @classmethod
    def parse(cls, obj: dict):
        return _model_override.get(cls, cls)(obj)


def override_model(model):
    def wrapper(new_model):
        if model in _model_override:
            raise MultipleOverrideError(
                f'Multiple overrides for {model}. This is almost certainly an error.'
                'If you ABSOLUTELY have a good reason for doing this, you should'
                'instead override the existing subclass of this model and let the'
                'resolution chain work deterministically. Any other use is assuredly'
                'going to land you in a world of pain.'
            )

        _model_override[model] = new_model

        return new_model

    return wrapper


def isinstance_or_none(obj, t):
    return obj is None or isinstance(obj, t)


class Node(Model):
    """The base node object, which encapsulates all node API responses"""

    def __init__(self, obj: dict):
        super().__init__(obj)

        self.node_type = obj['nodeType']
        assert isinstance(self.node_type, str)

        self.node_display_name = obj['nodeDisplayName']
        assert isinstance(self.node_display_name, str)

        self.results = obj['results']
        assert isinstance(self.results, list) or isinstance(self.results, dict) or self.results is None

        self.total_count = obj['totalCount']
        assert isinstance_or_none(self.total_count, int)

        self.next = obj['next']
        assert isinstance_or_none(self.next, str)


class Broadcaster(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.broadcaster_id = obj['broadcasterID']
        assert isinstance(self.broadcaster_id, str)

        self.service_times_are_preformatted = obj['serviceTimesArePreformatted']
        assert isinstance_or_none(self.service_times_are_preformatted, bool)

        self.service_times = obj['serviceTimes']
        assert isinstance_or_none(self.service_times, str)

        self.denomination = obj['denomination']
        assert isinstance_or_none(self.denomination, str)

        self.address = obj['address']
        assert isinstance_or_none(self.address, str)

        self.display_name = obj['displayName']
        assert isinstance(self.display_name, str)

        self.location = obj['location']
        assert isinstance(self.location, str)

        self.latitude = obj['latitude']
        assert isinstance_or_none(self.latitude, float)

        self.longitude = obj['longitude']
        assert isinstance_or_none(self.longitude, float)

        self.image_url = obj['imageURL']
        assert isinstance(self.image_url, str)

        self.album_art_url_format = obj['albumArtURL']
        assert isinstance(self.album_art_url_format, str)

        self.minister = obj['minister']
        assert isinstance_or_none(self.minister, str)

        self.phone = obj['phone']
        assert isinstance_or_none(self.phone, str)

        self.home_page_url = obj['homePageURL']
        assert isinstance_or_none(self.home_page_url, str)

        self.bible_version = obj['bibleVersion']
        assert isinstance_or_none(self.bible_version, str)

        self.facebook_username = obj['facebookUsername']
        assert isinstance_or_none(self.facebook_username, str)

        self.twitter_username = obj['twitterUsername']
        assert isinstance_or_none(self.twitter_username, str)

        self.about_us = obj['aboutUs']
        assert isinstance_or_none(self.about_us, str)

        self.webcast_in_progress = obj['webcastInProgress']
        assert isinstance(self.webcast_in_progress, bool)

        self.vacant_pulpit = obj['vacantPulpit']
        assert isinstance(self.vacant_pulpit, bool)

    def get_album_art_url(self, size: int):  # pragma: no cover
        """Returns a URL for the square album art with a with and height equal to the provided size argument"""
        return self.album_art_url_format.replace('{size}', str(size))

    def __str__(self):  # pragma: no cover
        return f'<Broadcaster {self.broadcaster_id} "{self.display_name}">'


class Speaker(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.display_name = obj['displayName']
        assert isinstance(self.display_name, str)

        self.sort_name = obj.get('sortName')
        assert isinstance(self.sort_name, str)

        self.bio = obj['bio']
        assert isinstance_or_none(self.bio, str)

        self.portrait_url = obj['portraitURL']
        assert isinstance(self.portrait_url, str)

        self.rounded_thumbnail_image_url = obj['roundedThumbnailImageURL']
        assert isinstance(self.rounded_thumbnail_image_url, str)

        self.album_art_url_format = obj['albumArtURL']
        assert isinstance(self.album_art_url_format, str)

        # The following are present on certain endpoints, such as filter_options
        if obj.get('mostRecentPreachDate'):
            self.most_recent_preach_date = datetime.datetime.strptime(obj['mostRecentPreachDate'], '%Y-%m-%d').date()
        else:
            self.most_recent_preach_date = None

        self.sermon_count = obj.get('sermonCount')
        assert isinstance_or_none(self.sermon_count, int)

    def get_album_art_url(self, size: int):  # pragma: no cover
        """Returns a URL for the square album art with a with and height equal to the provided size argument"""
        return self.album_art_url_format.replace('{size}', str(size))

    @property
    def is_generic(self) -> bool:
        return self.display_name in _generic_speaker_names


@enum.unique
class MediaClass(enum.Enum):
    AUDIO = 'audio'
    VIDEO = 'video'
    TEXT = 'text'

    ALL = 'all'


@enum.unique
class MediaType(enum.Enum):
    MP3 = 'mp3'
    AAC = 'aac'

    MP4 = 'mp4'

    PDF = 'pdf'
    WORD = 'doc'
    TRANSCRIPT = 'transcript'

    JPEG = 'jpg'

    ORIGINAL_AUDIO = 'orig-audio'
    ORIGINAL_VIDEO = 'orig-video'


class Media(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.media_type = MediaType(obj['mediaType'])
        assert isinstance(self.media_type, MediaType)

        self.is_live = obj['live']
        assert isinstance(self.is_live, bool)

        self.is_adaptive = obj['adaptiveBitrate']
        assert isinstance(self.is_adaptive, bool)

        self.stream_url = obj['streamURL']
        assert isinstance_or_none(self.stream_url, str)

        self.download_url = obj.get('downloadURL')
        assert isinstance_or_none(self.download_url, str)

        self.bitrate = obj['bitrate']
        assert isinstance_or_none(self.bitrate, int)

        self.duration = obj['duration']
        assert isinstance_or_none(self.duration, int)

        self.audio_codec = obj['audioCodec']
        assert isinstance_or_none(self.audio_codec, str)

        self.video_codec = obj['videoCodec']
        assert isinstance_or_none(self.video_codec, str)

        self.thumbnail_image_url = obj['thumbnailImageURL']
        assert isinstance_or_none(self.thumbnail_image_url, str)

        self.raw_url = obj.get('rawURL')
        assert isinstance_or_none(self.raw_url, str)


class MediaSet(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.audio = [Media.parse(rec) for rec in obj['audio']]
        self.video = [Media.parse(rec) for rec in obj['video']]
        self.text = [Media.parse(rec) for rec in obj['text']]


class Sermon(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.sermon_id = obj['sermonID']
        assert isinstance(self.sermon_id, str)

        self.broadcaster = Broadcaster.parse(obj['broadcaster'])
        self.speaker = Speaker.parse(obj['speaker'])

        self.full_title = obj['fullTitle']
        assert isinstance(self.full_title, str)

        self.display_title = obj['displayTitle']
        assert isinstance(self.display_title, str)

        self.subtitle = obj['subtitle']
        assert isinstance_or_none(self.subtitle, str)

        self.series = SermonSeries.parse(obj['series']) if obj.get('series') else None

        self.preach_date = datetime.datetime.strptime(obj['preachDate'], '%Y-%m-%d').date()
        assert isinstance(self.preach_date, datetime.date)

        try:
            self.staff_pick_date = datetime.datetime.strptime(obj['pickDate'], '%Y-%m-%d').date()
            assert isinstance_or_none(self.staff_pick_date, datetime.date)
        except (TypeError, ValueError):
            self.staff_pick_date = None

        timestamp = obj['publishTimestamp']
        self.publish_timestamp = datetime.datetime.fromtimestamp(timestamp, pytz.utc) if timestamp is not None else None

        self.language_code = obj['languageCode']
        assert isinstance(self.language_code, str)

        self.bible_text = obj['bibleText']
        assert isinstance_or_none(self.bible_text, str)

        self.more_info_text = obj['moreInfoText']
        assert isinstance_or_none(self.more_info_text, str)

        self.event_type = SermonEventType(obj['eventType'])

        self.download_count = obj['downloadCount']  # audio download count
        assert isinstance(self.download_count, int)

        self.video_download_count = obj['videoDownloadCount']
        assert isinstance(self.video_download_count, int)

        self.document_download_count = obj['documentDownloadCount']
        assert isinstance(self.document_download_count, int)

        self.external_link = obj['externalLink']
        assert isinstance_or_none(self.external_link, str)

        self.keywords = obj.get('keywords', [])

        self.media = MediaSet.parse(obj['media'])

    def __str__(self):  # pragma: no cover
        return f'<Speaker {self.speaker.display_name} - {self.display_title}>'


class Webcast(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.display_name = obj['displayName']
        assert isinstance(self.display_name, str)

        self.broadcaster_id = obj['broadcasterID']
        assert isinstance(self.broadcaster_id, str)

        self.source_location = obj['broadcasterLocation']
        assert isinstance(self.source_location, str)

        self.start_time = datetime.datetime.fromtimestamp(obj['startTime'], tz=pytz.utc)
        assert isinstance(self.start_time, datetime.datetime)

        self.preview_image_url = obj['previewImageURL']
        assert isinstance_or_none(self.preview_image_url, str)

        self.resizable_preview_image_url = obj['resizablePreviewImageURL']
        assert isinstance_or_none(self.resizable_preview_image_url, str)

        self.peak_listener_count = obj['peakListenerCount']
        assert isinstance(self.peak_listener_count, int)

        self.total_tune_in_count = obj['totalTuneInCount']
        assert isinstance(self.total_tune_in_count, int)

        self.media = MediaSet.parse(obj['media'])

    def __str__(self):  # pragma: no cover
        return f'<WebcastInfo {self.broadcaster_id} "{self.display_name}"">'


class RelativeBroadcasterLocation(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.broadcaster = Broadcaster.parse(obj['broadcaster'])
        assert isinstance(self.broadcaster, Broadcaster)

        self.meters = obj['meters']
        assert isinstance(self.meters, int)

    def __str__(self):  # pragma: no cover
        return f'<RelativeBroadcasterLocation {self.broadcaster.broadcaster_id} - ~{round(self.meters/1000, 1)}km away>'


class SermonSeries(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.title = obj['title']
        self.broadcaster_id = obj['broadcasterID']
        self.latest = datetime.datetime.strptime(obj['latest'][:10], '%Y-%m-%d') if obj['latest'] else None
        self.earliest = datetime.datetime.strptime(obj['earliest'][:10], '%Y-%m-%d') if obj['earliest'] else None
        self.count = obj['count']

    def __str__(self):  # pragma: no cover
        return f'<SermonSeries {self.title} ({self.count} sermons)>'


class SermonEventType(enum.Enum):
    AUDIO_BOOK = 'Audio Book'
    BIBLE_STUDY = 'Bible Study'
    CAMP_MEETING = 'Camp Meeting'
    CHAPEL_SERVICE = 'Chapel Service'
    CHILDREN = 'Children'
    CLASSIC_AUDIO = 'Classic Audio'
    CONFERENCE = 'Conference'
    CURRENT_EVENTS = 'Current Events'
    DEBATE = 'Debate'
    DEVOTIONAL = 'Devotional'
    FUNERAL_SERVICE = 'Funeral Service'
    MIDWEEK_SERVICE = 'Midweek Service'
    PODCAST = 'Podcast'
    PRAYER_MEETING = 'Prayer Meeting'
    Q_AND_A = 'Question & Answer'
    RADIO_BROADCAST = 'Radio Broadcast'
    SPECIAL_MEETING = 'Special Meeting'
    SUNDAY_AFTERNOON = 'Sunday Afternoon'
    SUNDAY_AM = 'Sunday - AM'
    SUNDAY_PM = 'Sunday - PM'
    SUNDAY_SCHOOL = 'Sunday School'
    SUNDAY_SERVICE = 'Sunday Service'
    TEACHING = 'Teaching'
    TESTIMONY = 'Testimony'
    TV_BROADCAST = 'TV Broadcast'
    VIDEO_DVD = 'Video DVD'
    WEDDING = 'Wedding'
    YOUTH = 'Youth'


class SermonEventTypeDetail(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.type = obj.get('type')
        self.description = obj.get('description')
        self.number_of_sermons = obj.get('numberOfSermons')
        self.roku_image_url = obj.get('rokuImageURL')
        self.fire_tv_image_url = obj.get('fireTVImageURL')
        self.number_of_sermons = obj.get('numberOfSermons')


@enum.unique
class SpurgeonDevotionalType(enum.Enum):
    AM = 'AM'  # Morning Devotional
    PM = 'PM'  # Evening Devotional
    CHECKBOOK = 'CHECKBOOK'  # Faith's Checkbook (note American spelling)


class SpurgeonDevotional(Model):
    def __init__(self, obj: dict):
        super().__init__(obj)

        self.type = SpurgeonDevotionalType(obj['type'])
        self.month = obj['month']
        self.day = obj['day']
        self.quote = obj['quote']
        self.reference = obj['reference']
        self.content = obj['content']
        self.audio = Sermon(obj['sermon'])

    def __str__(self):  # pragma: no cover
        return f'<SpurgeonDevotional for {self.month}/{self.day}>'


@enum.unique
class OSISBook(enum.Enum):
    GEN = 'GEN'
    EXO = 'EXO'
    LEV = 'LEV'
    NUM = 'NUM'
    DEU = 'DEU'
    JOS = 'JOS'
    JDG = 'JDG'
    RUT = 'RUT'
    _1SA = '1SA'
    _2SA = '2SA'
    _1KI = '1KI'
    _2KI = '2KI'
    _1CH = '1CH'
    _2CH = '2CH'
    EZR = 'EZR'
    NEH = 'NEH'
    EST = 'EST'
    JOB = 'JOB'
    PSA = 'PSA'
    PRO = 'PRO'
    ECC = 'ECC'
    SNG = 'SNG'
    ISA = 'ISA'
    JER = 'JER'
    LAM = 'LAM'
    EZK = 'EZK'
    DAN = 'DAN'
    HOS = 'HOS'
    JOL = 'JOL'
    AMO = 'AMO'
    OBA = 'OBA'
    JON = 'JON'
    MIC = 'MIC'
    NAM = 'NAM'
    HAB = 'HAB'
    ZEP = 'ZEP'
    HAG = 'HAG'
    ZEC = 'ZEC'
    MAL = 'MAL'
    MAT = 'MAT'
    MRK = 'MRK'
    LUK = 'LUK'
    JHN = 'JHN'
    ACT = 'ACT'
    ROM = 'ROM'
    _1CO = '1CO'
    _2CO = '2CO'
    GAL = 'GAL'
    EPH = 'EPH'
    PHP = 'PHP'
    COL = 'COL'
    _1TH = '1TH'
    _2TH = '2TH'
    _1TI = '1TI'
    _2TI = '2TI'
    TIT = 'TIT'
    PHM = 'PHM'
    HEB = 'HEB'
    JAS = 'JAS'
    _1PE = '1PE'
    _2PE = '2PE'
    _1JN = '1JN'
    _2JN = '2JN'
    _3JN = '3JN'
    JUD = 'JUD'
    REV = 'REV'


@enum.unique
class SermonSortOption(enum.Enum):
    DOWNLOADS = 'downloads'
    EVENT = 'event'
    LANGUAGE = 'language'
    LAST_PLAYED = 'lastplayed'
    NEWEST = 'newest'
    OLDEST = 'oldest'
    PICK_DATE = 'pickdate'
    SERIES = 'series'
    SPEAKER = 'speaker'


class Book(Model):
    """A book of the bible, and associated chapters that you can use to filter a broadcaster's content"""

    def __init__(self, obj: dict):
        super().__init__(obj)

        self.name = obj['bookName']
        self.chapters = obj['chapters']
        self.osis_pa = obj['osisPA']


class Language(Model):
    """A language that you can use to filter a broadcaster's content"""

    def __init__(self, obj: dict):
        super().__init__(obj)

        self.name = obj['languageName']
        self.iso_code = obj['languageCode']


class SermonCountForSpeaker(Model):
    """A speaker name, and how many sermons they preached at a broadcaster (used for filtering)"""

    def __init__(self, obj: dict):
        super().__init__(obj)

        self.count = obj['count']
        self.speaker_name = obj['speaker']


class FilterOptions(Model):
    """A set of various things that you can filter by.

    For example, which books and chapters of the Bible have content, which speakers
    have spoken at a given church/ministry, etc.
    """

    def __init__(self, obj: dict):
        super().__init__(obj)

        self.books = [Book.parse(rec) for rec in obj['bibleBooks']]
        self.languages = [Language.parse(rec) for rec in obj['languages']]
        self.series = [SermonSeries.parse(rec) for rec in obj['series']]
        self.speakers = [Speaker.parse(rec) for rec in obj['speakers']]
        self.sermon_counts_for_speakers = [SermonCountForSpeaker.parse(rec) for rec in obj['sermonCountsForSpeakers']]
        self.sermon_event_types = [SermonEventTypeDetail.parse(rec) for rec in obj['sermonEventTypes']]
        self.years: [int] = [rec['year'] for rec in obj['years']]  # This structure is simple enough to reduce


@enum.unique
class SeriesSortOrder(enum.Enum):
    LAST_UPDATED = 'last_updated'
    TITLE = 'title'
    SERMON_COUNT_HIGHEST = 'sermon_count_highest'
    SERMON_COUNT_LOWEST = 'sermon_count_lowest'
