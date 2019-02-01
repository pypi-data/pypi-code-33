from yandex_checkout.domain.common.base_object import BaseObject
from yandex_checkout.domain.models.amount import Amount


class ReceiptItem(BaseObject):
    """
    Class representing receipt item data wrapper object

    Used in Receipt
    """
    __description = None

    __quantity = None

    __amount = None

    __vat_code = None

    __payment_mode = None

    __payment_subject = None

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = str(value)

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, value):
        self.__quantity = float(value)

    @property
    def amount(self):
        return self.__amount

    @amount.setter
    def amount(self, value):
        if isinstance(value, dict):
            self.__amount = Amount(value)
        elif isinstance(value, Amount):
            self.__amount = value
        else:
            raise TypeError('Invalid amount value type')

    @property
    def vat_code(self):
        return self.__vat_code

    @vat_code.setter
    def vat_code(self, value):
        self.__vat_code = int(value)

    @property
    def payment_mode(self):
        return self.__payment_mode

    @payment_mode.setter
    def payment_mode(self, value):
        self.__payment_mode = str(value)

    @property
    def payment_subject(self):
        return self.__payment_subject

    @payment_subject.setter
    def payment_subject(self, value):
        self.__payment_subject = str(value)


class PaymentMode(object):
    """
    Class representing payment_mode values enum
    """
    FULL_PREPAYMENT = 'full_prepayment'
    PARTIAL_PREPAYMENT = 'partial_prepayment'
    ADVANCE = 'advance'
    FULL_PAYMENT = 'full_payment'
    PARTIAL_PAYMENT = 'partial_payment'
    CREDIT = 'credit'
    CREDIT_PAYMENT = 'credit_payment'


class PaymentSubject(object):
    """
    Class representing payment_subject values enum
    """
    COMMODITY = 'commodity'
    EXCISE = 'excise'
    JOB = 'job'
    SERVICE = 'service'
    GAMBLING_BET = 'gambling_bet'
    GAMBLING_PRIZE = 'gambling_prize'
    LOTTERY = 'lottery'
    LOTTERY_PRIZE = 'lottery_prize'
    INTELLECTUAL_ACTIVITY = 'intellectual_activity'
    PAYMENT = 'payment'
    AGENT_COMMISSION = 'agent_commission'
    COMPOSITE = 'composite'
    ANOTHER = 'another'
