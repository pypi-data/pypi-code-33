from datetime import datetime
from io import BytesIO
from typing import Optional, List, Tuple

from bzflag.networking.packet_not_set_error import PacketNotSetError
from bzflag.utilities.json_serializable import JsonSerializable
from bzflag.networking.packet import Packet


class GamePacket(JsonSerializable):
    __slots__ = (
        'packet_type',
        'packet',
        'buffer',
        'timestamp_offset',
    )

    def __init__(self):
        super().__init__()

        self.json_ignored: List[str] = ['buffer', 'packet']
        self.packet_type: str = ''
        self.packet: Optional[Packet] = None
        self.buffer: Optional[BytesIO] = None
        self.timestamp_offset: Optional[datetime] = None

    def _unpack(self) -> None:
        raise NotImplementedError

    def build(self) -> None:
        if self.packet is None:
            raise PacketNotSetError

        self.buffer = BytesIO(self.packet.data)
        self._unpack()
        self.buffer.close()

    def get_countdown_time(self) -> Tuple[int, int, int]:
        """
        Get representation of the current countdown time this packet occurred at.
        This value represents the amount of time that is left in this recording.

        :return: A tuple with the following values: hours, minutes, seconds
        """
        if self.packet is None:
            raise PacketNotSetError

        if self.timestamp_offset is None or self.packet.timestamp is None:
            return -1, -1, -1

        delta = self.timestamp_offset - self.packet.timestamp

        return delta.seconds // 3600, delta.seconds // 60, delta.seconds % 60

    @classmethod
    def factory(cls):
        return cls()
