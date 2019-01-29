from typing import Optional

from bzflag.networking.game_data_flag import FlagData
from bzflag.networking.game_packet import GamePacket
from bzflag.networking.network_message import code_from_chars
from bzflag.networking.packet import Packet


class MsgKilledPacket(GamePacket):
    __slots__ = (
        'victim_id',
        'killer_id',
        'reason',
        'shot_id',
        'flag',
        'physics_driver_id',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgKilled'
        self.victim_id: int = -1
        self.killer_id: int = -1
        self.reason: int = -1
        self.shot_id: int = -1
        self.flag: Optional[FlagData] = None
        self.physics_driver_id: int = -1

    def _unpack(self):
        self.victim_id = Packet.unpack_uint8(self.buffer)
        self.killer_id = Packet.unpack_uint8(self.buffer)
        self.reason = Packet.unpack_uint16(self.buffer)
        self.shot_id = Packet.unpack_uint16(self.buffer)
        self.flag = Packet.unpack_flag(self.buffer)

        if self.reason == code_from_chars('pd'):
            self.physics_driver_id = Packet.unpack_uint32(self.buffer)
