# -*- coding:utf-8 -*-
from pyramid.path import DottedNameResolver

from endi_payment.interfaces import IPaymentRecordHistoryService


def includeme(config):
    settings = config.get_settings()

    module_path = "endi_payment.history.HistoryLogService"

    key = "endi_payment.interfaces.IPaymentRecordHistoryService"
    if key in settings:
        module_path = settings[key]

    if module_path == "endi_payment.history.HistoryDBService":
        if 'endi_payment_db.url' not in settings:
            raise Exception(u"endi_payment.dev est à false et aucune url "
                            u"endi_payment_db.url n'est fourni")
        else:
            # We will store the endi payment's history
            config.include('.database')

    history_service = DottedNameResolver().resolve(module_path)

    config.register_service_factory(
        history_service, IPaymentRecordHistoryService
    )
