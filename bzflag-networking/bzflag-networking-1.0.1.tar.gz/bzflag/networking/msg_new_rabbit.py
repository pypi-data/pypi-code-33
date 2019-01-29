from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgNewRabbitPacket(GamePacket):
    __slots__ = (
        'player_id',
        'paused',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgNewRabbit'
        self.player_id: int = -1
        self.paused: int = -1

    def _unpack(self):
        self.player_id = Packet.unpack_uint8(self.buffer)
        self.paused = Packet.unpack_uint8(self.buffer)
