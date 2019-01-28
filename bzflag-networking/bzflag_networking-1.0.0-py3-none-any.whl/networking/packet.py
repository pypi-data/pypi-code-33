import math
import socket
import struct

from datetime import datetime, timezone
from io import BytesIO, BufferedIOBase
from typing import BinaryIO, Union, Tuple, Optional, Any

from bzflag.networking.game_data_firing_info import FiringInfoData
from bzflag.networking.game_data_flag import FlagData
from bzflag.networking.game_data_player_state import PlayerStateData, JumpJets, OnDriver, UserInputs, PlaySound
from bzflag.networking.game_data_shot import ShotData
from bzflag.networking.network_message import NetworkMessage
from bzflag.networking.unpackable import Unpackable
from bzflag.networking.network_protocol import Vector3F


small_scale = 32766.0
small_max_dist = 0.02 * small_scale
small_max_vel = 0.01 * small_scale
small_max_ang_vel = 0.001 * small_scale


class Packet(Unpackable):
    __slots__ = (
        'mode',
        'code',
        'length',
        'next_file_pos',
        'prev_file_pos',
        'timestamp',
        'data',
    )

    def __init__(self):
        self.mode: int = -1
        self.code: int = -1
        self.length: int = -1
        self.next_file_pos: int = -1
        self.prev_file_pos: int = -1
        self.timestamp: Optional[datetime] = None
        self.data: Any = None

    def unpack(self, buf: BinaryIO) -> None:
        chunk = BytesIO(buf.read(32))

        self.mode = Packet.unpack_uint16(chunk)
        self.code = Packet.unpack_uint16(chunk)
        self.length = Packet.unpack_uint32(chunk)
        self.next_file_pos = Packet.unpack_uint32(chunk)
        self.prev_file_pos = Packet.unpack_uint32(chunk)
        self.timestamp = Packet.unpack_timestamp(chunk)

        if self.length > 0:
            self.data = buf.read(self.length)
        else:
            self.data = None

    @staticmethod
    def unpack_int8(buf: BinaryIO) -> int:
        return Packet._unpack_int(buf, 1)

    @staticmethod
    def unpack_uint8(buf: BinaryIO) -> int:
        return Packet._unpack_int(buf, 1, False)

    @staticmethod
    def unpack_int16(buf: BinaryIO) -> int:
        return Packet._unpack_int(buf, 2)

    @staticmethod
    def unpack_uint16(buf: BinaryIO) -> int:
        return Packet._unpack_int(buf, 2, False)

    @staticmethod
    def unpack_int32(buf: BinaryIO) -> int:
        return Packet._unpack_int(buf, 4)

    @staticmethod
    def unpack_uint32(buf: BinaryIO) -> int:
        return Packet._unpack_int(buf, 4, False)

    @staticmethod
    def unpack_int64(buf: BinaryIO) -> int:
        return Packet._unpack_int(buf, 8)

    @staticmethod
    def unpack_uint64(buf: BinaryIO) -> int:
        return Packet._unpack_int(buf, 8, False)

    @staticmethod
    def unpack_string(buf: BinaryIO, length: int) -> str:
        raw = buf.read(length)
        return raw.strip(b'\x00').decode('utf-8')

    @staticmethod
    def unpack_ip_address(buf: BinaryIO) -> str:
        # This byte was reserved for differentiating between IPv4 and IPv6 addresses
        # However, since BZFlag only supports IPv4, this byte is skipped
        buf.read(1)

        # IP addresses are stored in network byte order (aka Little Endian)
        ip_as_int = int.from_bytes(buf.read(4), byteorder='little', signed=False)

        # Output the IP address as little-endian unsigned long
        #   https://docs.python.org/3/library/struct.html#format-strings
        return socket.inet_ntoa(struct.pack('<L', ip_as_int))

    @staticmethod
    def unpack_float(buf: BinaryIO) -> float:
        val: bytes = buf.read(4)

        if not val:
            return 0.0

        return struct.unpack('>f', val)[0]

    @staticmethod
    def unpack_vector(buf: BinaryIO) -> Vector3F:
        return (
            Packet.unpack_float(buf),
            Packet.unpack_float(buf),
            Packet.unpack_float(buf),
        )

    @staticmethod
    def unpack_flag(buf: BinaryIO) -> FlagData:
        flag = FlagData()

        flag.index = Packet.unpack_uint16(buf)
        flag.abbv = Packet.unpack_string(buf, 2)
        flag.status = Packet.unpack_uint16(buf)
        flag.endurance = Packet.unpack_uint16(buf)
        flag.owner = Packet.unpack_uint8(buf)
        flag.position = Packet.unpack_vector(buf)
        flag.launch_pos = Packet.unpack_vector(buf)
        flag.landing_pos = Packet.unpack_vector(buf)
        flag.flight_time = Packet.unpack_float(buf)
        flag.flight_end = Packet.unpack_float(buf)
        flag.initial_velocity = Packet.unpack_float(buf)

        return flag

    @staticmethod
    def unpack_firing_info(buf: BinaryIO) -> FiringInfoData:
        data: FiringInfoData = FiringInfoData()

        data.time_sent = Packet.unpack_float(buf)
        data.shot = Packet.unpack_shot(buf)
        data.flag = Packet.unpack_string(buf, 2)
        data.lifetime = Packet.unpack_float(buf)

        return data

    @staticmethod
    def unpack_shot(buf: BinaryIO) -> ShotData:
        shot = ShotData()

        shot.player_id = Packet.unpack_uint8(buf)
        shot.shot_id = Packet.unpack_uint16(buf)
        shot.position = Packet.unpack_vector(buf)
        shot.velocity = Packet.unpack_vector(buf)
        shot.delta_time = Packet.unpack_float(buf)
        shot.team = Packet.unpack_uint16(buf)

        return shot

    @staticmethod
    def unpack_player_state(buf: BinaryIO, code: int) -> PlayerStateData:
        # TODO see if `in_order` is necessary of if it can be removed safely
        in_order: int = Packet.unpack_uint32(buf)
        in_status: int = Packet.unpack_uint16(buf)

        state = PlayerStateData()

        if code == NetworkMessage.PlayerUpdate:
            state.position = Packet.unpack_vector(buf)
            state.velocity = Packet.unpack_vector(buf)
            state.azimuth = Packet.unpack_float(buf)
            state.angular_velocity = Packet.unpack_float(buf)
        else:
            Int3 = Tuple[int, int, int]

            pos: Int3 = (
                Packet.unpack_int16(buf),
                Packet.unpack_int16(buf),
                Packet.unpack_int16(buf),
            )
            vel: Int3 = (
                Packet.unpack_int16(buf),
                Packet.unpack_int16(buf),
                Packet.unpack_int16(buf),
            )
            azi: int = Packet.unpack_int16(buf)
            ang_vel: int = Packet.unpack_int16(buf)

            position = [0, 0, 0]
            velocity = [0, 0, 0]

            for i in range(0, 3):
                position[i] = (float(pos[i]) * small_max_dist) / small_scale
                velocity[i] = (float(vel[i]) * small_max_vel) / small_scale

            state.position = tuple(position)
            state.velocity = tuple(velocity)
            state.azimuth = (float(azi) * math.pi) / small_scale
            state.angular_velocity = (float(ang_vel) * small_max_ang_vel) / small_scale

        if in_status & JumpJets != 0:
            jump_jets = Packet.unpack_uint16(buf)
            state.jump_jets_scale = float(jump_jets) / small_scale

        if in_status & OnDriver != 0:
            # TODO this value is being read in as unsigned, but needs to be converted to signed...?
            # TODO fix this...
            state.physics_driver = Packet.unpack_uint32(buf)

        if in_status & UserInputs != 0:
            speed = Packet.unpack_uint16(buf)
            ang_vel = Packet.unpack_uint16(buf)

            state.user_speed = (float(speed) * small_max_vel) / small_scale
            state.user_ang_vel = (float(ang_vel) * small_max_ang_vel) / small_scale

        if in_status & PlaySound != 0:
            state.sounds = Packet.unpack_uint8(buf)

        return state

    @staticmethod
    def unpack_timestamp(buf: BinaryIO) -> datetime:
        msb: int = Packet.unpack_uint32(buf)
        lsb: int = Packet.unpack_uint32(buf)

        ts_raw = (msb << 32) + lsb
        ts_float = ts_raw / 1000000

        return datetime.fromtimestamp(ts_float, timezone.utc)

    @staticmethod
    def _unpack_int(buf: Union[BinaryIO, BufferedIOBase], size: int, signed: bool = True) -> int:
        return int.from_bytes(buf.read(size), byteorder='big', signed=signed)
