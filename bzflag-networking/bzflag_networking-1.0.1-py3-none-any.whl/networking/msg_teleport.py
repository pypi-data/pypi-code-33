from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgTeleportPacket(GamePacket):
    __slots__ = (
        'player_id',
        'from_',
        'to',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgTeleport'
        self.player_id: int = -1
        self.from_: int = -1
        self.to: int = -1

    def _unpack(self):
        self.player_id = Packet.unpack_uint8(self.buffer)
        self.from_ = Packet.unpack_uint16(self.buffer)
        self.to = Packet.unpack_uint16(self.buffer)
