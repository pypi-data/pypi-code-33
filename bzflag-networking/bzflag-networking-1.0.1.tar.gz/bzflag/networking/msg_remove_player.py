from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgRemovePlayerPacket(GamePacket):
    __slots__ = (
        'player_id',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgRemovePlayer'
        self.player_id: int = -1

    def _unpack(self):
        self.player_id = Packet.unpack_uint8(self.buffer)
