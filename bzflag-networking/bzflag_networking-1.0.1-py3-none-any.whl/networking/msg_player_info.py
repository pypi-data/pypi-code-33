from typing import List

from bzflag.networking.game_data_player import PlayerData, IsRegistered, IsVerified, IsAdmin
from bzflag.networking.game_packet import GamePacket
from bzflag.networking.packet import Packet


class MsgPlayerInfoPacket(GamePacket):
    __slots__ = (
        'players',
    )

    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgPlayerInfo'
        self.players: List[PlayerData] = []

    def _unpack(self):
        count: int = Packet.unpack_uint8(self.buffer)

        for i in range(0, count):
            player = PlayerData()
            player.player_id = Packet.unpack_uint8(self.buffer)

            properties: int = Packet.unpack_uint8(self.buffer)

            player.is_registered = properties & IsRegistered == IsRegistered
            player.is_verified = properties & IsVerified == IsVerified
            player.is_admin = properties & IsAdmin == IsAdmin

            self.players.append(player)
