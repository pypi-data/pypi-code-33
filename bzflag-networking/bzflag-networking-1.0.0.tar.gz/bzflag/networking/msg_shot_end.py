from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgShotEndPacket(GamePacket):
    __slots__ = (
        'player_id',
        'shot_id',
        'reason',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgShotEnd'
        self.player_id: int = -1
        self.shot_id: int = -1
        self.reason: int = -1

    def _unpack(self):
        self.player_id = Packet.unpack_uint8(self.buffer)
        self.shot_id = Packet.unpack_uint16(self.buffer)
        self.reason = Packet.unpack_int16(self.buffer)
