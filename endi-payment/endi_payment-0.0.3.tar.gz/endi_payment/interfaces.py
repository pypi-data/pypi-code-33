# -*- coding: utf-8 -*-
from zope.interface import Interface


class IPaymentRecordHistoryService(Interface):
    """
    History manipulation tool iinterface for Payment action log
    """

    def record_action(self, action, invoice, payment):
        """
        History manipulation tool for Payment registration
        """
        pass
