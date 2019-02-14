#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
from django.conf import settings

try:
    from m3 import OperationResult
    from m3.actions import ActionPack, ACD, Action
except ImportError:
    from m3.ui.actions import ActionPack, ACD, Action, OperationResult

from production_request.utils import register_logger


PRODUCTION_REQUEST_CLIENT_LOGGER = register_logger(
    'production_request_client',
    formatter=logging.Formatter("%(message)s"))


class ProductionRequestPack(ActionPack):
    """
    Пак для работы с логами production_request
    """

    url = '/production-request'

    def __init__(self):
        super(ProductionRequestPack, self).__init__()

        self.action_save_client_log = SaveLogAction()

        self.actions.extend([
            self.action_save_client_log,
        ])


class SaveLogAction(Action):
    """
    Сохранение лога
    """
    url = '/save-client-log'

    def context_declaration(self):
        return [
            ACD('logs', type=object, required=True, default=[]),
        ]

    def run(self, request, context):
        if settings.PRODUCTION_REQUEST_LOG_CLIENT:
            for log_str in context.logs:
                PRODUCTION_REQUEST_CLIENT_LOGGER.info(json.dumps(log_str))

        return OperationResult()
