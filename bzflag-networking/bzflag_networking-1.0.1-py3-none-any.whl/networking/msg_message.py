from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgMessagePacket(GamePacket):
    __slots__ = (
        'player_from_id',
        'player_to_id',
        'message',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgMessage'
        self.player_from_id: int = -1
        self.player_to_id: int = -1
        self.message: str = ''

    def _unpack(self):
        self.player_from_id = Packet.unpack_uint8(self.buffer)
        self.player_to_id = Packet.unpack_uint8(self.buffer)
        self.message = Packet.unpack_string(self.buffer, -1)
