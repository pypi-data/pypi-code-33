import subprocess
from swdl.labels import Label
import m3u8
import urllib
import re
from datetime import datetime


class FFMPegRunner(object):
    """
    Usage:
        runner = FFMpegRunner()
        def status_handler(old, new):
            print "From {0} to {1}".format(old, new)
        runner.run('ffmpeg -i ...', status_handler=status_handler)
    """

    def run(self, command, status_handler=None):
        pipe = subprocess.Popen(command,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True)

        duration = None
        position = None
        new_pos = 0

        while True:
            line = pipe.stdout.readline().strip()

            if line == '' and pipe.poll() is not None:
                print("I am here")
                break

            if duration is None:
                duration = self.find_duration(line)

            if duration:
                new_pos = self.find_position(line)
                if new_pos:
                    if new_pos != position:
                        position = new_pos
                        if callable(status_handler):
                            status_handler(position, duration)

    @staticmethod
    def find_duration(line):
        re_duration = re.compile(
            '.*Duration: (\d{2}):(\d{2}):(\d{2}).(\d{2})[^\d]*',
            re.U)
        duration_match = re_duration.match(line)
        if duration_match:
            return FFMPegRunner.time2sec(duration_match)

    @staticmethod
    def find_position(line):
        re_position = re.compile('.*time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})\d*',
                                 re.U | re.I)
        position_match = re_position.match(line)
        if position_match:
            return FFMPegRunner.time2sec(position_match)

    @staticmethod
    def time2sec(search):
        secs = sum([int(search.group(i+1))*60**(2-i) for i in range(3)])

        return secs


class SWLoginError(Exception):
    pass


class NoEndlistError(Exception):
    pass


class NoPlaylistError(Exception):
    pass


class Match:
    """
    Class to store match information

    # Attributes
    matchId(str,int): Match id
    swcsId(str,int): The camera id
    name(str): The name of the match. Mostly "TeamA-TeamB"
    location(str): The location where the match took place
    userStreamLink(str): A download link for the user stream
    gridStreamLink(str):A download link for the grid stream
    state(str): Status of the stream. Can be created, live or done
    # Members
    labels(Label): #Label object that stores the labels
    """
    def __init__(self,
                 match_id,
                 camera_id="",
                 location="",
                 state="",
                 club_a_name="",
                 club_b_name="",
                 date = None):
        self.match_id = match_id
        self.camera_id = camera_id
        self.location = location
        self.state = state
        self.user_stream_link = "https://storage.googleapis.com/sw-sc-de-shared/{0}/720p/{0}.m3u8".format(match_id)
        self.grid_stream_link = "https://storage.googleapis.com/sw-sc-de-shared/{0}/Grid/{0}.m3u8".format(match_id)
        self.team_name_home = club_a_name
        self.team_name_away = club_b_name
        self.date = date
        self.labels = Label()
        self.data_service = None
        self.last_label_update = None

    @classmethod
    def from_json(cls,
                  RowKey,
                  swcsID="",
                  location="",
                  state="",
                  clubAName="",
                  clubBName="",
                  expectedStartTime="0",
                  *args,
                  **kwargs):
        match_id = str(RowKey)
        camera_id = str(swcsID)
        if expectedStartTime is not None:
            date = datetime.fromtimestamp(float(expectedStartTime)/1000)
        else:
            date = datetime.fromtimestamp(0)
        return Match(match_id, camera_id, location, state, clubAName, clubBName,
                     date)

    def copy_info(self, match):
        """
        Copys the info from another match

        # Arguments
        match(Match):
        """
        self.match_id = match.match_id
        self.camera_id = match.camera_id
        self.location = match.location
        self.state = match.state
        self.user_stream_link = match.user_stream_link
        self.grid_stream_link = match.grid_stream_link

    def download_user_stream(self, download_directory="."):
        """
        Downloads the user stream from the match. Needs ffmpeg

        # Attributes
        download_directory(str):

        # Raises
        NoPlaylistError: If video file is not existing
        NoEndlistError: If stream has not endlist tag. This means the stream is
        not correctly finished and can note be downlaoded with ffmpeg
        """
        self._download_match(download_directory, "User")

    def download_grid_stream(self, download_directory="."):
        """
        Downloads the grid stream from the match. Needs ffmpeg

        # Attributes
        download_directory:

        # Raises
        NoPlaylistError: If video file is not existing
        NoEndlistError: If stream has not endlist tag. This means the stream is
        not correctly finished and can note be downlaoded with ffmpeg
        """
        self._download_match(download_directory, "Grid")

    def pull_info(self):
        """
        Updates match info

        # Raises
        SWLoginError
        """
        if not self.data_service:
            raise SWLoginError("Not logged into Soccerwatch Data Service")
        m = self.data_service.pull_info(self)
        self.copy_info(m)

    def pull_labels(self,
                    time_from=None,
                    virtual_camera_id="-1"):
        """
        Updates match labels.
        Warning: May override all locally stored labels

        #Arguments
        time_from (datetime,int): Will only get labels later than this time,
        Must be msecs after 1970 or datetime
        virtual_camera_id (str): Camera Id
        source (str): "human" or "machine"

        # Raises
        SWLoginError: If data service was not connected
        """
        if not self.data_service:
            raise SWLoginError("Not logged into Soccerwatch Data Service")
        m = self.data_service.pull_labels(self, time_from, virtual_camera_id)
        self.labels = m.labels
        self.last_label_update = m.last_label_update

    def push_labels(self,
                    start_index=0,
                    virtual_camera_id="-1",
                    source="human"):
        """
        Uploads the labels to the cloud

        # Arguments
        start_index (int): Only positions greater than start index will be
        pushed
        virtual_camera_id (str): Camera id the positions belongs to
        source (str): Should be "human" or "machine"

        # Raises
        SWLoginError: If data service was not connected
        """
        if not self.data_service:
            raise SWLoginError("Not logged into Soccerwatch Data Service")
        self.data_service.push_labels(self, start_index, virtual_camera_id,
                                      source)

    def set_data_service(self, data_service):
        """
        Sets the #DataService for this match

        # Arguments
        data_service(DataService):
        """
        self.data_service = data_service
        return self

    def grid_stream_available(self):
        """
        Checks if a user stream is available

        # Returns
        bool: if available
        """
        return self._check_stream("User")

    def user_stream_available(self):
        """
        Checks if a user stream is available

        # Returns
        bool: if available
        """
        return self._check_stream("Grid")

    def user_stream_has_endlist(self):
        """
        Checks if user stream has an an endlist tag, which means that the
        stream has been completely uploaded

        # Returns

        bool: True if endlist is exsisting
        """
        return self._check_endlist("User")

    def grid_stream_has_endlist(self):
        """
        Checks if grid stream has an an endlist tag, which means that the
        stream has been completely uploaded

        # Returns

        bool: True if endlist is exsisting
        """
        return self._check_endlist("Grid")

    def _check_stream(self, streamType="User"):
        if streamType == "User":
            download_link = self.user_stream_link
        else:
            download_link = self.grid_stream_link
        try:
            m3u8.load(download_link)
        except urllib.error.HTTPError:
            return False
        return True

    def _check_endlist(self, streamType="User"):
        if streamType == "User":
            download_link = self.user_stream_link
        else:
            download_link = self.grid_stream_link
        try:
            playlist = m3u8.load(download_link)
            if not playlist.is_endlist:
                return False
        except urllib.error.HTTPError:
            return False
        return True

    def _download_match(self, download_directory=".", streamType="User"):
        hint = ""
        if streamType == "User":
            hint = "user"
            download_link = self.user_stream_link
        else:
            hint="grid"
            download_link = self.grid_stream_link
        # Check m3u8
        try:
           playlist = m3u8.load(download_link)
           if not playlist.is_endlist:
               raise NoEndlistError("Video has no endlist, can not be downloaded with FFMPEG")
        except urllib.error.HTTPError:
               raise NoPlaylistError("Playlist was not found")
        command = "ffmpeg -i {} -c copy -y \"{}/{}_{}_{}.mp4\"".format(download_link,
                                                                   download_directory,
                                                                   self.match_id,
                                                                   self.name,
                                                                   hint)
        print(command)
        def run_callback(actual,total):
            percent = 100.0*actual/total
            print("%.2f%%"%percent)

        ffmpeg = FFMPegRunner()
        ffmpeg.run(command, status_handler=run_callback)

    def add_player_position(self, timestamp, players):
        """
        Uploads the player positions to the cloud

        # Arguments
        timestamp (int): Current timestamp in seconds
        players (str): 2D integer tensor 25x5: playerId, teamId, x, y, confidence. If playerId is -1, player is not valid.
        x, y and confidence should be scaled between 0 and 1000

        # Raises
        SWLoginError: If data service was not connected
        """
        self.labels.player_positions[timestamp] = players
        if not self.data_service:
            raise SWLoginError

        self.data_service.upload_player_positions(timestamp, self)




    def __str__(self):
        return "Match[\n\tid:\t\t{}\n\tcamera:\t\t{}\n\tlocation:\t{}\n\tstate:\t\t{}\n\tdate:\t\t{}\n" \
               "\thome:\t\t{}\n\taway:\t\t{}\n\tvideo:\t\t{}\n\tgrid:\t\t{}]".format(
            self.match_id,
            self.camera_id,
            self.location,
            self.state,
            self.date,
            self.team_name_home,
            self.team_name_away,
            self.user_stream_link,
            self.grid_stream_link)
