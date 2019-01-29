from typing import Optional

from bzflag.networking.game_data_flag import FlagData
from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgTransferFlagPacket(GamePacket):
    __slots__ = (
        'from_',
        'to',
        'flag',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgTransferFlag'
        self.from_: int = -1
        self.to: int = -1
        self.flag: Optional[FlagData] = None

    def _unpack(self):
        self.from_ = Packet.unpack_uint8(self.buffer)
        self.to = Packet.unpack_uint8(self.buffer)
        self.flag = Packet.unpack_flag(self.buffer)
