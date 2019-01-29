from typing import List

from bzflag.networking.game_data_player_info import PlayerInfo
from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgAdminInfoPacket(GamePacket):
    __slots__ = (
        'players',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgAdminInfo'
        self.players: List[PlayerInfo] = []

    def _unpack(self):
        count: int = Packet.unpack_uint8(self.buffer)

        for i in range(0, count):
            Packet.unpack_uint8(self.buffer)

            p_info: PlayerInfo = PlayerInfo()
            p_info.player_index = Packet.unpack_uint8(self.buffer)
            p_info.ip_address = Packet.unpack_ip_address(self.buffer)

            self.players.append(p_info)
