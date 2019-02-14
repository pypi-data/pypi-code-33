import logging
import mpv
import youtube_dl
import datetime
import re
import pathlib

from ts3ekkoutil.envconsts import EkkoPropertyNames as epn

try:
    from ts3ekkosingle.event_type import EventType
    from ts3ekkosingle.errors import EkkoUnsuitedCommand, EkkoNonexistentAlias, EkkoInvalidLocalMedia
    from ts3ekkosingle.argparser import NonExitParser, MediaAliasParser, UtilityParser
except ImportError:
    from ..event_type import EventType
    from ..errors import EkkoUnsuitedCommand, EkkoNonexistentAlias, EkkoInvalidLocalMedia
    from ..argparser import NonExitParser, MediaAliasParser, UtilityParser

logger = logging.getLogger('ekkocog-mediaalias')


class MediaCogPermission:
    QUEUE = 'media.queue.append'
    SKIP = 'media.queue.skip'
    MEDIA = 'media.queue.media'
    MEDIA_QUEUE = 'media.queue.media_queue'
    CLEAR_QUEUE = 'media.queue.clear'
    SHUFFLE_QUEUE = 'media.queue.shuffle'
    PAUSE = 'media.pause'
    RESUME = 'media.resume'

    VOLUME_SET = 'media.volume.set'
    VOLUME_GET = 'media.volume.get'
    VOLUME_RESET = 'media.volume.reset'

class TrackMeta:
    def __init__(self, uri):
        self._uri = uri
        self.info_dict = None

    def _ensure_info_dict(self):
        if self.info_dict is None:
            logger.debug(f'dict_info for uri={self.uri} not a available, downloading')
            try:
                with youtube_dl.YoutubeDL() as ytdl:
                    self.info_dict = ytdl.extract_info(self.uri, download=False)
                    logger.debug(self.info_dict)
            except:
                self.info_dict = {}

    @property
    def uri(self):
        if self._uri.startswith('ytdl://'):
            return f'https://youtu.be/{self._uri[len("ytdl://"):]}'
        else:
            return self._uri

    @property
    def title(self):
        self._ensure_info_dict()
        return self.info_dict.get('title', self.uri)

    @property
    def bbcode_formatted(self):
        if self.is_local_file:
            return self.uri
        else:
            return f'[url={self.uri}]{self.title}[/url]'

    @property
    def is_local_file(self):
        return not self.uri.startswith('https://') and not self.uri.startswith('http://')


class MediaCog:
    def __init__(self, ekkobot, args):
        self.ekko_bot = ekkobot

        self._volume_modifier = args[epn.COG_MEDIA_VOLUME_MODIFIER]
        self._volume_max = args[epn.COG_MEDIA_VOLUME_MAX]

        self.media_directory = args[epn.EKKO_MEDIA_DIRECTORY]

        # create mpv player
        self.mpv = mpv.MPV(ytdl=True)
        # this is a music bot, not a video bot! no need to spend resources on video.
        self.mpv.vid = False
        # callback to remove played tracks from mpv playlist
        self.mpv.event_callback('end-file')(self._remove_played_track)

        # cache for track metadata (title, etc)
        self.trackmeta_cache = {}

        # Init volume at a 'safe' level
        self._reset_volume()

    @property
    def commands(self):
        """
        Returns data for command hooks creation for events like mediaalias set/get, etc.
        
        :return list of tuple in format: (EventType-int, callback-func, priority-int, name-str, help_cmd_str-str)
        """
        return [
            (EventType.TEXTMESSAGE, self.cmd_queue, 100, None, '!queue'),
            (EventType.TEXTMESSAGE, self.cmd_skip, 100, None, '!skip'),
            (EventType.TEXTMESSAGE, self.cmd_media, 100, None, '!media'),
            (EventType.TEXTMESSAGE, self.cmd_pausemedia, 100, None, '!pausemedia'),
            (EventType.TEXTMESSAGE, self.cmd_resumemedia, 100, None, '!resumemedia'),
            (EventType.TEXTMESSAGE, self.cmd_clearqueue, 100, None, '!clearqueue'),
            (EventType.TEXTMESSAGE, self.cmd_shuffle, 100, None, '!shuffle'),
            (EventType.TEXTMESSAGE, self.cmd_volume, 75, None, '!volume'),
            (EventType.TEXTMESSAGE, self.cmd_volume_set, 100, None, '!volume'),
            (EventType.TEXTMESSAGE, self.cmd_volume_get, 100, None, '!volume'),
            (EventType.TEXTMESSAGE, self.cmd_volumereset, 100, None, '!volume'),
        ]

    @staticmethod
    def _remove_url_bbcode(dirty):
        """
        Removes the `[URL]` and `[/URL]` BB-Code from a string.
        
        :param dirty: string or list to be cleared
        :return: string or list without the URL BB-Code
        """
        if type(dirty) == str:
            return re.sub("\[\/?[uU][rR][lL]\]", '', dirty)
        elif type(dirty) == list:
            return [re.sub("\[\/?[uU][rR][lL]\]", '', uri) for uri in dirty]

    def _reset_volume(self):
        """
        Resets the mpv volume.
        """
        self.mpv.volume = (self._volume_max * self._volume_modifier) * 0.5

    def _remove_played_track(self, event):
        """
        Remove played tracks from mpv playlist.
        
        :param event: the mpv event which creates the call to this function
        """
        logger.debug(f'_remove_played_track {event}')
        logger.debug(f'_remove_played_track pre-removal playlist: {self.mpv.playlist}')
        logger.debug(f'_remove_played_track pre-removal playlist_pos: {self.mpv.playlist_pos}')
        for index in range(0, self.mpv.playlist_pos or 1):
            if self.mpv.playlist and not self.mpv.playlist[0].get('current', False):
                self.mpv.playlist_remove(0)
                logger.debug(f'_remove_played_track post-removal playlist: {self.mpv.playlist}')
                logger.debug(f'_remove_played_track post-removal playlist_pos: {self.mpv.playlist_pos}')

    def _media_info_queue(self, end=None):
        """
        Creates and formats text-output of all currently queued tracks.
        
        :param end: maximum amount of listed tracks
        :return: bb-code formatted output string
        """
        output = 'Currently queued tracks:\n'
        for index in range(self.mpv.playlist_pos or 0, end or len(self.mpv.playlist or [])):
            try:
                uri = self.mpv.playlist[index]['filename']
                trackmeta = self._request_trackmeta(uri)
                output += f'{trackmeta.bbcode_formatted}\n'
            except IndexError:
                break
        if self.mpv.playlist_pos is None:
            output += 'No track queued or playing!'
        return output.strip('\n')

    def _media_info_current(self):
        """
        Creates and formats text-output for the currently playing track.
        
        :return: bb-code formatted output string
        """
        if self.mpv.playlist_pos is not None:
            uri = self.mpv.playlist[self.mpv.playlist_pos]['filename']
            trackmeta = self._request_trackmeta(uri)
            try:
                td_remaining = datetime.timedelta(seconds=self.mpv.playtime_remaining)
                formatted_remaining = self.format_seconds(td_remaining.seconds)
                td_played = datetime.timedelta(seconds=self.mpv.playback_time)
                formatted_played = self.format_seconds(td_played.seconds)
            except TypeError:
                return f'{trackmeta.bbcode_formatted}'
            else:
                return f'{trackmeta.bbcode_formatted} - {formatted_played} played, {formatted_remaining} remaining'
        else:
            return 'No track queued or playing!'

    @staticmethod
    def format_seconds(seconds: int):
        """
        Formats an amount of seconds into a mm:ss format. If in hour-range, also add hours in front (h:mm:ss)
        
        :param seconds: amount of seconds to be formatted
        :type seconds: int
        :return: string in h:mm:ss format.
        """
        result = ''
        if seconds // 3600 > 0:
            result += f'{seconds//3600}:'
        result += f'{str(seconds%3600//60).zfill(2)}:{str(seconds%60).zfill(2)}'
        return result

    @staticmethod
    def resolve_mediafile_path(media_directory, file):
        """
        Resolves relative path/file name inside the configured media directory.
        
        :param media_directory: media directory root path
        :param file: file name of the to be resolved file
        :return: absolute path of the requested file
        :raises: EkkoInvalidLocalMedia on invalid file name
        """
        media_directory_path = pathlib.Path(media_directory).resolve()
        # TODO: yeah, would be nice to have glob support for local fs | Problem: single uri -> multiple uri
        # media_paths = [mp.resolve for mp in media_directory_path.glob(file)]
        media_path = media_directory_path / file
        media_path = media_path.resolve()

        # check if resolved path is also in the configured media directory and actually exists
        # => prevent fs index creation/info acquirement
        for fragment in media_path.parents:
            if fragment == media_directory_path and media_path.exists():
                return str(media_path)

        # apparently it violates something (existing/in jail), so lets raise an eception
        raise EkkoInvalidLocalMedia(file)

    def _request_trackmeta(self, uri: str):
        """
        Provides TrackMeta object for requested track. Tries to fetch from cache first, otherwise creates.

        :param uri: requested track
        :return: TrackMeta object
        """
        trackmeta = self.trackmeta_cache.get(uri, None)

        if trackmeta is None:
            # not in cache, lets create and cache it!
            trackmeta = TrackMeta(uri)
            self.trackmeta_cache[uri] = trackmeta

        return trackmeta

    def playlist_append(self, uris, pos):
        """
        Inserts tracks into the requested position in the mpv playlist.
        Adjusts mpv playlist_pos accordingly if necessary.

        Should multiple tracks be inserted the pos param marks the position of the first insert and
        others will be inserted afterwards.

        :param uris: list of uris to be inserted into the playlist.
        :param pos: position where to tracks should be inserted. None = append.
        """

        for index, uri in enumerate(uris):
            uri = self._remove_url_bbcode(uri)

            if TrackMeta(uri).is_local_file:
                try:
                    uri = self.resolve_mediafile_path(self.media_directory, uri)
                except EkkoInvalidLocalMedia as e:
                    logger.error(e)
                    continue

            logger.debug(f'adding "{uri}" to playlist')

            self.mpv.playlist_append(uri)

            if self.mpv.playlist_pos is None:
                logger.debug('playlist_pos is none, setting to 0')
                self.mpv.playlist_pos = 0

            if pos is not None:
                logger.debug('pos is not none, modifying playlist order')
                last_index = len(self.mpv.playlist) - 1
                self.mpv.playlist_move(last_index, self.mpv.playlist_pos + pos + index)

                # if new pos is 0, fix the playlist_pos
                if pos == 0:
                    self.mpv.playlist_pos = 0

        logger.debug(self.mpv.playlist)

    def cmd_skip(self, event):
        """
        Command: !skip

        Skips a given number of tracks (default 1) in the playlist.

        See `MediaAliasParser.parse_skip` for parameters.

        :param event: TS3Event
        """
        cmd_prefix = '!skip'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix}', event[0]['msg']):
            if self.ekko_bot.can(MediaCogPermission.SKIP, event):
                count = self.ekko_bot.parse(MediaAliasParser.parse_skip, event, cmd_prefix, event[0]['msg'])
                playlist_length = len(self.mpv.playlist or [])
                if playlist_length <= count:
                    # lib does not have a method for stop, so lets access mpv more directly.
                    self.mpv.command('stop')
                else:
                    self.mpv.playlist_pos += count

    def cmd_queue(self, event):
        """
        Command: !queue

        Queues a given track into the playlist.

        See `MediaAliasParser.parse_queue` for parameters.

        :param event: TS3Event
        """
        cmd_prefix = '!queue'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix} ', event[0]['msg']):
            if self.ekko_bot.can(MediaCogPermission.QUEUE, event):
                pos, uris = self.ekko_bot.parse(MediaAliasParser.parse_queue, event, cmd_prefix, event[0]['msg'])
                uris = self._remove_url_bbcode(uris)
                self.playlist_append(uris, pos)

    def cmd_media(self, event):
        """
        Command: !media

        Queries metadata about media in the playlist.

        See `MediaAliasParser.parse_media` for parameters.

        :param event: TS3Event
        """
        cmd_prefix = '!media'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix}(\s*$|\s+\w+)', event[0]['msg']):
            query_type = self.ekko_bot.parse(MediaAliasParser.parse_media, event, cmd_prefix, event[0]['msg'],
                                             description='Show information about current media. '
                                                         'If `queue` keyword is specifed, show information about '
                                                         'the next few queued tracks.')
            if query_type == 'queue':
                if self.ekko_bot.can(MediaCogPermission.MEDIA_QUEUE, event):
                    self.ekko_bot.reply(self._media_info_queue(5), event)
            else:
                if self.ekko_bot.can(MediaCogPermission.MEDIA, event):
                    self.ekko_bot.reply(self._media_info_current(), event)

    def cmd_pausemedia(self, event):
        """
        Command: !pausemedia

        Pauses media playback.

        :param event: TS3Event
        """
        cmd_prefix = '!pausemedia'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix}', event[0]['msg']):
            if self.ekko_bot.can(MediaCogPermission.PAUSE, event):
                self.ekko_bot.parse(UtilityParser.parse_noargs, event, cmd_prefix, event[0]['msg'],
                                    description='Pause the current playing media.')
                self.mpv.pause = True
                self.ekko_bot.reply('Playback paused. Resume with "!resumemedia".', event)

    def cmd_resumemedia(self, event):
        """
        Command: !resumemedia

        Resumes media playback.

        :param event: TS3Event
        """
        cmd_prefix = '!resumemedia'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix}', event[0]['msg']):
            if self.ekko_bot.can(MediaCogPermission.RESUME, event):
                self.ekko_bot.parse(UtilityParser.parse_noargs, event, cmd_prefix, event[0]['msg'],
                                    description='Resume playing the previously paused media.')
                self.mpv.pause = False
                self.ekko_bot.reply('Playback resumed. Pause with "!pausemedia".', event)

    def cmd_clearqueue(self, event):
        """
        Command: !clearqueue

        Removes all not-playing tracks from the queue. Does not stop the current playing track.

        :param event: TS3Event
        """
        cmd_prefix = '!clearqueue'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix}', event[0]['msg']):
            if self.ekko_bot.can(MediaCogPermission.CLEAR_QUEUE, event):
                self.ekko_bot.parse(UtilityParser.parse_noargs, event, cmd_prefix, event[0]['msg'],
                                    description='Clear the playlist queue and remove all currently not playing'
                                                ' tracks from it.')
                self.mpv.playlist_clear()
                self.ekko_bot.reply('Queue cleared.', event)

    def cmd_shuffle(self, event):
        """
        Command: !shuffle

        Shuffles the current playlist.

        :param event: TS3Event
        """
        cmd_prefix = '!shuffle'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix}', event[0]['msg']):
            if self.ekko_bot.can(MediaCogPermission.SHUFFLE_QUEUE, event):
                self.ekko_bot.parse(UtilityParser.parse_noargs, event, cmd_prefix, event[0]['msg'],
                                    description='Shuffles all currently queued tracks.')
                self.mpv.command('playlist-shuffle')
                # After playlist-shuffle, the current playing track will not be found at playlist_pos=0 anymore, but will
                # have a new position inside the playlist. To not have all tracks between playlist_pos=0 and current
                # playlist_pos removed by `_remove_played_track`, we quickly want to put back the current playing song
                # at position 0.
                self.mpv.playlist_move(self.mpv.playlist_pos, 0)
                self.ekko_bot.reply('Queue shuffled.', event)

    def cmd_volumereset(self, event):
        """
        Command: !volume reset

        Resets the volume to the default value.

        :param event: TS3Event
        """
        cmd_prefix = '!volume reset'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix}', event[0]['msg']):
            if self.ekko_bot.can(MediaCogPermission.VOLUME_RESET, event):
                self.ekko_bot.parse(UtilityParser.parse_noargs, event, cmd_prefix, event[0]['msg'],
                                    description='Reset the volume to the default level.')
                self._reset_volume()
                self.ekko_bot.reply('Volume reset.', event)

    def cmd_volume(self, event):
        """
        Command: !volume [-h|--help]

        Fallback command in case none of the other !volume commands catches on, replies with usage information.

        :param event: TS3Event
        """
        cmd_prefix = '!volume'
        cmd_usage = 'usage: !volume [new volume] \n    get current volume: !volume\n    set new volume: !volume 100'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix}\s*(-h|--help)\s*$', event[0]['msg']):
            self.ekko_bot.reply(cmd_usage, event)

    def cmd_volume_get(self, event):
        """
        Command: !volume

        Replies with current volume value.

        :param event: TS3Event
        """
        cmd_prefix = '!volume'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix}\s*$', event[0]['msg']):
            if self.ekko_bot.can(MediaCogPermission.VOLUME_GET, event):
                self.ekko_bot.reply(f'Current volume: {self.mpv.volume / self._volume_modifier}', event)

    def cmd_volume_set(self, event):
        """
        Command: !volume <value>

        Sets the volume to the given value.

        :param event: TS3Event
        """
        cmd_prefix = '!volume'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix} \d+\s*$', event[0]['msg']):
            if self.ekko_bot.can(MediaCogPermission.VOLUME_SET, event):
                volume = self.ekko_bot.parse(MediaAliasParser.parse_volume, event, cmd_prefix, event[0]['msg'])
                if volume < self._volume_max:
                    self.mpv.volume = volume * self._volume_modifier
                else:
                    self.mpv.volume = self._volume_max * self._volume_modifier
                self.ekko_bot.reply(f'Volume set to {self.mpv.volume / self._volume_modifier}.', event)
