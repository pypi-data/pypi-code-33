from bzflag.networking.game_data_player_score import PlayerScore
from bzflag.networking.game_packet import GamePacket
from bzflag.networking.network_protocol import NetworkProtocol
from bzflag.networking.packet import Packet


class MsgAddPlayerPacket(GamePacket):
    __slots__ = (
        'player_index',
        'player_type',
        'team_value',
        'callsign',
        'motto',
        'score',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgAddPlayer'

        self.player_index: int = -1
        self.player_type: int = -1
        self.team_value: int = -1
        self.score: PlayerScore = PlayerScore()
        self.callsign: str = ''
        self.motto: str = ''

    def _unpack(self):
        self.player_index = Packet.unpack_uint8(self.buffer)
        self.player_type = Packet.unpack_uint16(self.buffer)
        self.team_value = Packet.unpack_uint16(self.buffer)
        self.score.wins = Packet.unpack_uint16(self.buffer)
        self.score.losses = Packet.unpack_uint16(self.buffer)
        self.score.team_kills = Packet.unpack_uint16(self.buffer)

        self.callsign = Packet.unpack_string(self.buffer, NetworkProtocol.CALLSIGN_LEN)
        self.motto = Packet.unpack_string(self.buffer, NetworkProtocol.MOTTO_LEN)
