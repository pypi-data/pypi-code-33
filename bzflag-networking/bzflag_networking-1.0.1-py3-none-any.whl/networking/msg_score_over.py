from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgScoreOverPacket(GamePacket):
    __slots__ = (
        'player_id',
        'team',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgScoreOver'
        self.player_id: int = -1
        self.team: int = -1

    def _unpack(self):
        self.player_id = Packet.unpack_uint8(self.buffer)
        self.team = Packet.unpack_uint16(self.buffer)
