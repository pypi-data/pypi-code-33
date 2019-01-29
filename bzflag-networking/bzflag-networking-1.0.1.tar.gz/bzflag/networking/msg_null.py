from bzflag.networking.game_packet import GamePacket


class MsgNullPacket(GamePacket):
    def __init__(self):
        super().__init__()

        self.packet_type: str = 'MsgNull'

    def _unpack(self):
        pass
