# -*- coding: utf-8 -*-
"""
Public Tools are defined here
"""
from autonomie.models.task.invoice import Payment
from endi_payment.interfaces import IPaymentRecordHistoryService


class PaymentService(object):
    """
    A class grouping all the public methods

    record_payment

        Record a new payment

    modifiy_payment

        Modify an existing payment


    delete_payment

        Delete an existing payment
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.dbsession = request.dbsession
        self.history = request.find_service(IPaymentRecordHistoryService)

    def add(self, invoice, params):
        """
        Record a payment for the given invoice

        :param obj invoice: The Invoice associated to this transaction
        :param **params: List of parameters used to record a payment

        :returns: The generated Payment object id
        :rtype: int
        """
        payment = Payment()
        for key, value in params.items():
            setattr(payment, key, value)
        payment.user_id = self.request.user.id
        invoice.payments.append(payment)
        self.dbsession.merge(invoice)
        self.dbsession.flush()
        self.history.record(
            "ADD",
            invoice,
            payment,
        )
        return payment

    def update(self, payment, params):
        """
        Modify the given Payment instance
        :param obj invoice: The Invoice associated to this transaction
        :param **params: List of parameters used to record a payment

        :returns: The modified Payment object id
        :rtype: int
        """
        for key, value in params.items():
            setattr(payment, key, value)
        payment = self.dbsession.merge(payment)

        self.history.record(
            "UPDATE",
            payment.task,
            payment,
        )
        return payment

    def delete(self, payment):
        """
        Delete the given Payment instance

        :param obj invoice: The Invoice associated to this transaction

        :returns: True/False if the deletion succeeded
        :rtype: bool
        """
        self.dbsession.delete(payment)
        self.dbsession.flush()
        self.history.record(
            "DELETE",
            payment.task,
            payment,
        )
        return True
