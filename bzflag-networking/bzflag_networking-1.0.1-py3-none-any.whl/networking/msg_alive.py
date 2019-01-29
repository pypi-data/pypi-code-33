from bzflag.networking.game_packet import GamePacket
from bzflag.networking.network_protocol import Vector3F
from bzflag.networking.packet import Packet


class MsgAlivePacket(GamePacket):
    __slots__ = (
        'player_id',
        'position',
        'azimuth',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgAlive'
        self.player_id: int = -1
        self.position: Vector3F = [0, 0, 0]
        self.azimuth: float = 0.0

    def _unpack(self):
        self.player_id = Packet.unpack_uint8(self.buffer)
        self.position = Packet.unpack_vector(self.buffer)
        self.azimuth = Packet.unpack_float(self.buffer)
