from typing import Optional

from bzflag.networking.game_data_player_state import PlayerStateData
from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgPlayerUpdatePacket(GamePacket):
    __slots__ = (
        'timestamp',
        'player_id',
        'state',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgPlayerUpdate'
        self.timestamp: float = 0.0
        self.player_id: int = -1
        self.state: Optional[PlayerStateData] = None

    def _unpack(self):
        self.timestamp = Packet.unpack_float(self.buffer)
        self.player_id = Packet.unpack_uint8(self.buffer)
        self.state = Packet.unpack_player_state(self.buffer, self.packet.code)
