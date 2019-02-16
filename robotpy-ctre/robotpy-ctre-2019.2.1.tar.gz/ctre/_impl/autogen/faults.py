from ..faultsbase import FaultsBase


class CANifierFaults(FaultsBase):
    __slots__ = ()


class CANifierStickyFaults(FaultsBase):
    __slots__ = ()


class Faults(FaultsBase):
    __slots__ = ()

    @property
    def underVoltage(self) -> bool:
        return self.bits & (1 << 0) != 0

    @property
    def forwardLimitSwitch(self) -> bool:
        return self.bits & (1 << 1) != 0

    @property
    def reverseLimitSwitch(self) -> bool:
        return self.bits & (1 << 2) != 0

    @property
    def forwardSoftLimit(self) -> bool:
        return self.bits & (1 << 3) != 0

    @property
    def reverseSoftLimit(self) -> bool:
        return self.bits & (1 << 4) != 0

    @property
    def hardwareFailure(self) -> bool:
        return self.bits & (1 << 5) != 0

    @property
    def resetDuringEn(self) -> bool:
        return self.bits & (1 << 6) != 0

    @property
    def sensorOverflow(self) -> bool:
        return self.bits & (1 << 7) != 0

    @property
    def sensorOutOfPhase(self) -> bool:
        return self.bits & (1 << 8) != 0

    @property
    def hardwareESDReset(self) -> bool:
        return self.bits & (1 << 9) != 0

    @property
    def remoteLossOfSignal(self) -> bool:
        return self.bits & (1 << 10) != 0

    @property
    def apiError(self) -> bool:
        return self.bits & (1 << 11) != 0


class StickyFaults(FaultsBase):
    __slots__ = ()

    @property
    def underVoltage(self) -> bool:
        return self.bits & (1 << 0) != 0

    @property
    def forwardLimitSwitch(self) -> bool:
        return self.bits & (1 << 1) != 0

    @property
    def reverseLimitSwitch(self) -> bool:
        return self.bits & (1 << 2) != 0

    @property
    def forwardSoftLimit(self) -> bool:
        return self.bits & (1 << 3) != 0

    @property
    def reverseSoftLimit(self) -> bool:
        return self.bits & (1 << 4) != 0

    @property
    def resetDuringEn(self) -> bool:
        return self.bits & (1 << 5) != 0

    @property
    def sensorOverflow(self) -> bool:
        return self.bits & (1 << 6) != 0

    @property
    def sensorOutOfPhase(self) -> bool:
        return self.bits & (1 << 7) != 0

    @property
    def hardwareESDReset(self) -> bool:
        return self.bits & (1 << 8) != 0

    @property
    def remoteLossOfSignal(self) -> bool:
        return self.bits & (1 << 9) != 0

    @property
    def apiError(self) -> bool:
        return self.bits & (1 << 10) != 0


class PigeonIMU_Faults(FaultsBase):
    __slots__ = ()


class PigeonIMU_StickyFaults(FaultsBase):
    __slots__ = ()

