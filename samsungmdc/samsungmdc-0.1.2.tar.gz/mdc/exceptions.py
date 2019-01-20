"""Provide useful exceptions for MDC protocol."""


class SourceNotExist(Exception):
    """Source do not exist."""

    pass


class InvalidVolume(Exception):
    """Invalid volume value."""

    pass


class VideoWallNotSupported(Exception):
    """Video Wall not supported."""

    pass
