from enum import Enum


class BlockchainEnv(Enum):
    UA_SERVER = 'ua_server'
    AWS = 'aws'
    LOCAL = 'local'
    CUSTOM = 'custom'
