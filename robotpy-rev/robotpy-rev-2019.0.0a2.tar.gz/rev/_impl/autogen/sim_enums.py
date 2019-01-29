import enum


class LimitSwitch(enum.Enum):
    kForward = 0
    kReverse = 1


class LimitSwitchPolarity(enum.Enum):
    kNormallyOpen = 0
    kNormallyClosed = 1


class CANError(enum.Enum):
    kOK = 0
    kError = 1
    kTimeout = 2


class MotorType(enum.Enum):
    kBrushed = 0
    kBrushless = 1


class ParameterStatus(enum.Enum):
    kOK = 0
    kInvalidID = 1
    kMismatchType = 2
    kAccessMode = 3
    kInvalid = 4
    kNotImplementedDeprecated = 5


class ConfigParameter(enum.Enum):
    kCanID = 0
    kInputMode = 1
    kMotorType = 2
    kCommAdvance = 3
    kSensorType = 4
    kCtrlType = 5
    kIdleMode = 6
    kInputDeadband = 7
    kFirmwareVer = 8
    kHallOffset = 9
    kPolePairs = 10
    kCurrentChop = 11
    kCurrentChopCycles = 12
    kP_0 = 13
    kI_0 = 14
    kD_0 = 15
    kF_0 = 16
    kIZone_0 = 17
    kDFilter_0 = 18
    kOutputMin_0 = 19
    kOutputMax_0 = 20
    kP_1 = 21
    kI_1 = 22
    kD_1 = 23
    kF_1 = 24
    kIZone_1 = 25
    kDFilter_1 = 26
    kOutputMin_1 = 27
    kOutputMax_1 = 28
    kP_2 = 29
    kI_2 = 30
    kD_2 = 31
    kF_2 = 32
    kIZone_2 = 33
    kDFilter_2 = 34
    kOutputMin_2 = 35
    kOutputMax_2 = 36
    kP_3 = 37
    kI_3 = 38
    kD_3 = 39
    kF_3 = 40
    kIZone_3 = 41
    kDFilter_3 = 42
    kOutputMin_3 = 43
    kOutputMax_3 = 44
    kReserved = 45
    kOutputRatio = 46
    kSerialNumberLow = 47
    kSerialNumberMid = 48
    kSerialNumberHigh = 49
    kLimitSwitchFwdPolarity = 50
    kLimitSwitchRevPolarity = 51
    kHardLimitFwdEn = 52
    kHardLimitRevEn = 53
    kSoftLimitFwdEn = 54
    kSoftLimitRevEn = 55
    kRampRate = 56
    kFollowerID = 57
    kFollowerConfig = 58
    kSmartCurrentStallLimit = 59
    kSmartCurrentFreeLimit = 60
    kSmartCurrentConfig = 61
    kSmartCurrentReserved = 62
    kMotorKv = 63
    kMotorR = 64
    kMotorL = 65
    kMotorRsvd1 = 66
    kMotorRsvd2 = 67
    kMotorRsvd3 = 68
    kEncoderCountsPerRev = 69
    kEncoderAverageDepth = 70
    kEncoderSampleDelta = 71


class ParameterType(enum.Enum):
    kInt32 = 0
    kUint32 = 1
    kFloat32 = 2
    kBool = 3


class PeriodicFrame(enum.Enum):
    kStatus0 = 0
    kStatus1 = 1
    kStatus2 = 2


class SensorType(enum.Enum):
    kNoSensor = 0
    kHallSensor = 1
    kEncoder = 2
    kSensorless = 3


class IdleMode(enum.Enum):
    kCoast = 0
    kBrake = 1


class InputMode(enum.Enum):
    kPWM = 0
    kCAN = 1


class FaultID(enum.Enum):
    kBrownout = 0
    kOvercurrent = 1
    kOvervoltage = 2
    kMotorFault = 3
    kSensorFault = 4
    kStall = 5
    kEEPROMCRC = 6
    kCANTX = 7
    kCANRX = 8
    kHasReset = 9
    kDRVFault = 10
    kOtherFault = 11
    kSoftLimitFwd = 12
    kSoftLimitRev = 13
    kHardLimitFwd = 14
    kHardLimitRev = 15


class ControlType(enum.Enum):
    kDutyCycle = 0
    kVelocity = 1
    kVoltage = 2
    kPosition = 3

