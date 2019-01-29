from typing import Tuple

Vector3F = Tuple[float, float, float]


class NetworkProtocol:
    CALLSIGN_LEN = 32
    MOTTO_LEN = 128
    SERVER_LEN = 8
    MESSAGE_LEN = 128
    HASH_LEN = 64
    WORLD_SETTING_SIZE = 30
