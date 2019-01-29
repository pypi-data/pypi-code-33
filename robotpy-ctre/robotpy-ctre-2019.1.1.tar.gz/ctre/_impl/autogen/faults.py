from ..faultsbase import FaultsBase


class CANifierFaults(FaultsBase):
    __slots__ = (
    )

class CANifierStickyFaults(FaultsBase):
    __slots__ = (
    )

class Faults(FaultsBase):
    __slots__ = (
        'underVoltage',
        'forwardLimitSwitch',
        'reverseLimitSwitch',
        'forwardSoftLimit',
        'reverseSoftLimit',
        'hardwareFailure',
        'resetDuringEn',
        'sensorOverflow',
        'sensorOutOfPhase',
        'hardwareESDReset',
        'remoteLossOfSignal',
        'aPIError',
    )

class StickyFaults(FaultsBase):
    __slots__ = (
        'underVoltage',
        'forwardLimitSwitch',
        'reverseLimitSwitch',
        'forwardSoftLimit',
        'reverseSoftLimit',
        'resetDuringEn',
        'sensorOverflow',
        'sensorOutOfPhase',
        'hardwareESDReset',
        'remoteLossOfSignal',
        'aPIError',
    )

class PigeonIMU_Faults(FaultsBase):
    __slots__ = (
    )

class PigeonIMU_StickyFaults(FaultsBase):
    __slots__ = (
    )
