"""Provide a class to send command to TV."""
import socket

from . import exceptions


class Mdc():
    """Implement the MDC protocol."""

    def __init__(self, ip=None, port=1515, mdc_id=0xFE):
        """Initialize class with ip, port and mdc ID.

        By default, MDC protocol listen on port 1515.
        We can use MDC ID 0xFE for globing.
        """
        self._id = mdc_id
        self._ip = ip
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """Connect the socket to the remote TV."""
        self._socket.connect((self._ip, self._port))

    def send_command(self, command_id, *args):
        """Send a command to the remote TV."""
        command = [0xAA, command_id, self._id, len(args)] + list(args)
        checksum = sum(command[1:]) % 256
        command.append(checksum)
        self._socket.send(bytes(command))

    def power_off(self):
        """Power off the remote TV."""
        self.send_command(0x11, 0x0)

    def power_on(self):
        """Power on the remote TV."""
        self.send_command(0x11, 0x1)

    def set_source(self, source_id):
        """Set the source of the remote TV.

        The source_id value could be one of the following value :
        - 0x14: PC
        - 0x1E: BNC
        - 0x18: DVI
        - 0x0C: AV
        - 0x04: S-Video
        - 0x08: Component
        - 0x20: MagicNet
        - 0x30: RF(TV)
        - 0x40: DTV
        - 0x21: HDMI 1
        - 0x23: HDMI 2
        - 0x25: DisplayPort in
        """
        available_sources = [
            0x14, 0x1E, 0x18, 0x0C, 0x04, 0x08,
            0x20, 0x30, 0x40, 0x21, 0x23, 0x25
        ]
        if source_id not in available_sources:
            raise exceptions.SourceNotExist()
        self.send_command(0x14, source_id)

    def set_volume(self, volume):
        """Set the volume of the remote TV."""
        if volume < 0 or volume > 100:
            raise exceptions.InvalidVolume()
        self.send_command(0x12, volume)

    def mute_on(self):
        """Mute the remote TV."""
        self.send_command(0x13, 0x1)

    def mute_off(self):
        """Unmute the remote TV."""
        self.send_command(0x13, 0x0)

    def video_wall_on(self):
        """Enable video wall for the current source."""
        self.send_command(0x84, 0x1)

    def video_wall_off(self):
        """Disable video wall for the current source."""
        self.send_command(0x84, 0x0)

    def set_video_wall(self, nb_row, nb_col, pos):
        """Configure the video wall position for the current source.

        The protocol do not support more than 25 TV (5 x 5).
        If nb_row is set to 0, video wall will be disabled.
        """
        if nb_row < 0 or nb_row > 5:
            raise exceptions.VideoWallNotSupported()
        if nb_col < 1 or nb_col > 5:
            raise exceptions.VideoWallNotSupported()
        if pos < 1 or pos > 25:
            raise exceptions.VideoWallNotSupported()
        wall_div = nb_row << 4 | nb_col
        if nb_row == 0:
            wall_div = 0x00
        self.send_command(0x89, wall_div, pos)

    def is_powered_on(self):
        self.send_command(0x11)
        print("Is Powered On")
        # return self._socket.recv(1024)
        while 1:
            data = self._socket.recv(1024)
            return data


