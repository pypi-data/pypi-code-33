from enum import IntEnum
from typing import Optional


class ErrorCode(IntEnum):
    Success = 0,

    # Common errors

    # Caller passed invalid value as param 1 (null, invalid json and etc..)
    CommonInvalidParam1 = 100,

    # Caller passed invalid value as param 2 (null, invalid json and etc..)
    CommonInvalidParam2 = 101,

    # Caller passed invalid value as param 3 (null, invalid json and etc..)
    CommonInvalidParam3 = 102,

    # Caller passed invalid value as param 4 (null, invalid json and etc..)
    CommonInvalidParam4 = 103,

    # Caller passed invalid value as param 5 (null, invalid json and etc..)
    CommonInvalidParam5 = 104,

    # Caller passed invalid value as param 6 (null, invalid json and etc..)
    CommonInvalidParam6 = 105,

    # Caller passed invalid value as param 7 (null, invalid json and etc..)
    CommonInvalidParam7 = 106,

    # Caller passed invalid value as param 8 (null, invalid json and etc..)
    CommonInvalidParam8 = 107,

    # Caller passed invalid value as param 9 (null, invalid json and etc..)
    CommonInvalidParam9 = 108,

    # Caller passed invalid value as param 10 (null, invalid json and etc..)
    CommonInvalidParam10 = 109,

    # Caller passed invalid value as param 11 (null, invalid json and etc..)
    CommonInvalidParam11 = 110,

    # Caller passed invalid value as param 12 (null, invalid json and etc..)
    CommonInvalidParam12 = 111,

    # Invalid library state was detected in runtime. It signals library bug
    CommonInvalidState = 112,

    # Object (group, key, point, and etc...) passed by library caller has invalid structure
    CommonInvalidStructure = 113,


class IndyCryptoError(Exception):
    # error_code: ErrorCode
    # message: str - human-readable error description
    # indy_crypto_backtrace: Optional[str] - error backtrace.
    #         Collecting of backtrace can be enabled by:
    #             1) setting environment variable `RUST_BACKTRACE=1`

    def __init__(self, error_code: ErrorCode, message: str, indy_crypto_backtrace: Optional[str]):
        self.error_code = error_code
        self.message = message
        self.indy_backtrace = indy_crypto_backtrace
