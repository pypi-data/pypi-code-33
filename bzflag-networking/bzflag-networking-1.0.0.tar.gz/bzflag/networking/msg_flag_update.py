from typing import List

from bzflag.networking.game_data_flag import FlagData
from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgFlagUpdatePacket(GamePacket):
    __slots__ = (
        'flags',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgFlagUpdate'
        self.flags: List[FlagData] = []

    def _unpack(self):
        count: int = Packet.unpack_uint16(self.buffer)

        for i in range(0, count):
            flag = Packet.unpack_flag(self.buffer)
            self.flags.append(flag)
