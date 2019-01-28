from typing import List

from bzflag.networking.game_data_score import ScoreData
from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgScorePacket(GamePacket):
    __slots__ = (
        'scores',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgScore'
        self.scores: List[ScoreData] = []

    def _unpack(self):
        count: int = Packet.unpack_uint8(self.buffer)

        for i in range(0, count):
            data: ScoreData = ScoreData()
            data.player_id = Packet.unpack_uint8(self.buffer)
            data.wins = Packet.unpack_uint16(self.buffer)
            data.losses = Packet.unpack_uint16(self.buffer)
            data.team_kills = Packet.unpack_uint16(self.buffer)

            self.scores.append(data)
