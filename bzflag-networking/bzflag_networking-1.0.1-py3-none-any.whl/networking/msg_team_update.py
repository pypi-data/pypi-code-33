from typing import List

from bzflag.networking.game_data_team import TeamData
from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgTeamUpdatePacket(GamePacket):
    __slots__ = (
        'teams',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgTeamUpdate'
        self.teams: List[TeamData] = []

    def _unpack(self):
        count: int = Packet.unpack_uint8(self.buffer)

        for i in range(0, count):
            data: TeamData = TeamData()

            data.team = Packet.unpack_uint16(self.buffer)
            data.size = Packet.unpack_uint16(self.buffer)
            data.wins = Packet.unpack_uint16(self.buffer)
            data.losses = Packet.unpack_uint16(self.buffer)

            self.teams.append(data)
