from bzflag.utilities.json_serializable import JsonSerializable


class ReplayDuration(JsonSerializable):
    __slots__ = [
        'as_seconds',
        'days',
        'hours',
        'minutes',
        'seconds',
        'usecs',
    ]

    def __init__(self, timestamp: int):
        """
        A developer-friendly representation of microseconds

        :param timestamp: The duration of the recording in microseconds
        """
        super().__init__()

        secs = timestamp / 1000000

        day_len = 24 * 60 * 60
        self.days = int(secs / day_len)
        secs = secs % day_len

        hour_len = 60 * 60
        self.hours = int(secs / hour_len)
        secs = secs % hour_len

        min_len = 60
        self.minutes = int(secs / min_len)
        secs = secs % min_len

        self.seconds = int(secs)
        self.usecs = int(timestamp % 1000000)

        # Short cut for accessing this duration in seconds
        self.as_seconds = (self.days * day_len) + (self.hours * hour_len) + (self.minutes * min_len) + self.seconds
