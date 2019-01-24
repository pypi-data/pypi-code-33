from enum import Enum


class ResultStatus(Enum):
    SUCCEED = 'Succeed'
    FAILED = 'Failed'
    PENDING = 'Pending'


class EventType(Enum):
    PAYMENT_CREATE = 'payment.payment.create'
    CHARGE_CREATE = 'payment.charge.create'
