from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgTimeUpdatePacket(GamePacket):
    __slots__ = (
        'time_left',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgTimeUpdate'
        self.time_left: int = -1

    def _unpack(self):
        self.time_left = Packet.unpack_int32(self.buffer)
