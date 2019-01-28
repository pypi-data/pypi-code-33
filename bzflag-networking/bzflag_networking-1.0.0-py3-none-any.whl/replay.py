from datetime import timedelta
from typing import BinaryIO, List

from bzflag.networking.game_packet import GamePacket
from bzflag.networking.game_packet_mapping import GamePacketMap
from bzflag.utilities.json_serializable import JsonSerializable
from bzflag.networking.network_message import NetworkMessage, chars_from_code
from bzflag.networking.packet import Packet
from bzflag.replay_header import ReplayHeader


class Replay(JsonSerializable):
    __slots__ = (
        'header',
        'start_time',
        'end_time',
        'packets',
        'errors',
    )

    def __init__(self, file: str):
        self.header: ReplayHeader = ReplayHeader()
        self.packets: List[GamePacket] = []
        self.errors: List[str] = []

        with open(file, 'rb') as replay_file:
            self.header.unpack(replay_file)
            self._calc_timestamps(replay_file)
            self._load_packets(replay_file)

    def _calc_timestamps(self, buf: BinaryIO) -> None:
        # We want to load the first packet (a null packet) so we can get its
        # timestamp
        packet: Packet = Packet()
        packet.unpack(buf)

        self.start_time = packet.timestamp
        self.end_time = packet.timestamp + timedelta(microseconds=self.header.file_time)

    def _load_packets(self, buf: BinaryIO) -> None:
        # We've loaded the replay header already, so let's save the current
        # starting position for the packets
        packets_start = buf.tell()

        # Get the full file size and save it
        buf.seek(0, 2)
        file_size = buf.tell()

        # Go back to the start of the packets so we can read them in
        buf.seek(packets_start)

        while True:
            packet = Packet()
            packet.unpack(buf)

            try:
                msg_code = NetworkMessage(packet.code)
                game_packet = GamePacketMap[msg_code]()
                game_packet.packet = packet
                game_packet.timestamp_offset = self.end_time
                game_packet.build()

                self.packets.append(game_packet)
            except KeyError:
                game_code: str = chars_from_code(packet.code)
                self.errors.append(f'Unsupported game packet code: {game_code}')

            # We've reached the end of the replay
            if buf.tell() == file_size:
                break
