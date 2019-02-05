#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import uuid
from datetime import datetime
from psutil import Process

from django.conf import settings
from django.db import connections

from m3_legacy.middleware import get_thread_data

from production_request.enums import SqlOperationEnum
from production_request.utils import (
    ms_from_timedelta, get_client_ip, register_logger)


PRODUCTION_REQUEST_LOGGER = register_logger(
    'production_request',
    formatter=logging.Formatter("%(message)s"))

PRODUCTION_REQUEST_ENTER_LOGGER = register_logger(
    'production_request_enter',
    formatter=logging.Formatter("%(message)s"))


class ProductionRequestLoggingMiddleware(object):
    """
    Middleware для логирования запросов на production.
    Использует данные из production_request.database.CursorWrapper
    """
    # Атрибуты, не добавляемые в хэдеры
    exclude_attr_headers = ('uuid',)

    def process_request(self, request):
        self._start_log_request(request)

    def process_response(self, request, response):
        log_row = self._end_log_request(request)
        self._add_response_headers(request, response, log_row)

        return response

    def process_exception(self, request, exception):
        self._log_request(request)

    def _start_log_request(self, request):
        """
        Начинает процесс логирования запроса
        """
        request_uuid = request.META.get(
            'HTTP_PR_UUID',
            str(uuid.uuid4())[-12:]
        )
        request.production_request_uuid = request_uuid

        if settings.PRODUCTION_REQUEST:
            thread_data = get_thread_data()
            thread_data.production_request_uuid = request_uuid

            request.started_at = datetime.now()

            if settings.PRODUCTION_REQUEST_LOG_MEMORY:
                memory = self._get_memory_info()

                request.production_request_uss = memory.uss
                request.production_request_pss = memory.pss
                request.production_request_swap = memory.swap
                request.production_request_rss = memory.rss

        if settings.PRODUCTION_REQUEST_LOG_ENTER:
            self._log_enter(request_uuid, request.path)

    def _log_enter(self, request_uuid, request_path):
        """Логирует момент входа запроса в приложение"""
        self._log_state('enter', request_uuid, request_path)

    def _log_state(self, state, request_uuid, request_path):
        """Логирует определенный момент запроса"""
        PRODUCTION_REQUEST_ENTER_LOGGER.info({
            'uuid': request_uuid,
            'path': request_path,
            'state': state,
            'pid': os.getpid(),
            'timestamp': str(datetime.now()),
        })

    def _end_log_request(self, request):
        """Логирует параметры запроса и результаты обработки"""
        row = None
        _uuid = request.production_request_uuid

        if settings.PRODUCTION_REQUEST:
            try:
                process_request_time = ms_from_timedelta(
                    datetime.now() - request.started_at
                )
                process_sql_time = connections['default'].sql_time.pop(
                    request.production_request_uuid, float())

                sql_count = connections['default'].sql_count.pop(
                    request.production_request_uuid, 0)

                row = {
                    'uuid': _uuid,
                    'started': str(
                        request.started_at
                    ),
                    'path': request.path,
                    'user': str(request.user.id or ''),
                    'total': '{:.4f}'.format(process_request_time),
                    'sql_total': '{:.4f}'.format(process_sql_time),
                    'sql_count': str(sql_count),
                    'client_ip': get_client_ip(
                        request
                    ),
                    'pid': str(os.getpid())
                }

                # количестов sql-запросов в разрезе типов
                for operation in SqlOperationEnum.values:
                    operation_attr = 'sql_{}_count'.format(operation)
                    counter = getattr(
                        connections['default'],
                        operation_attr,
                        {}
                    )
                    row[operation_attr] = counter.pop(
                        request.production_request_uuid, 0
                    )

                if settings.PRODUCTION_REQUEST_LOG_MEMORY:
                    memory = self._get_memory_info()

                    row['uss'] = '{:.2f}'.format(
                        self._get_memory_diff(
                            request.production_request_uss,
                            memory.uss
                        )
                    )
                    row['pss'] = '{:.2f}'.format(
                        self._get_memory_diff(
                            request.production_request_pss,
                            memory.pss
                        )
                    )
                    row['swap'] = '{:.2f}'.format(
                        self._get_memory_diff(
                            request.production_request_swap,
                            memory.swap
                        )
                    )
                    row['rss'] = '{:.2f}'.format(
                        self._get_memory_diff(
                            request.production_request_rss,
                            memory.rss
                        )
                    )

                if settings.PRODUCTION_REQUEST_LOG_SERVER:
                    PRODUCTION_REQUEST_LOGGER.info(
                        row
                    )
            except Exception as err:
                if settings.PRODUCTION_REQUEST_LOG_SERVER:
                    PRODUCTION_REQUEST_LOGGER.error(
                        str(
                            err
                        )
                    )

        if settings.PRODUCTION_REQUEST_LOG_ENTER:
            self._log_exit(_uuid, request.path)

        return row

    def _get_memory_info(self):
        """Возвращает данные о памяти процесса"""
        return Process(os.getpid()).memory_full_info()

    def _get_memory_diff(self, m_begin, m_end):
        """Возвращает разницу размера памяти в МБ"""
        return (m_end - m_begin) / 1024 / 1024 / 8

    def _log_exit(self, request_uuid, request_path):
        """Логирует момент выхода запроса в приложение"""
        self._log_state('exit', request_uuid, request_path)

    def _add_response_headers(self, request, response, log_row):
        if settings.PRODUCTION_REQUEST_LOG_CLIENT:
            try:
                _uuid = request.production_request_uuid
                _started = request.META.get(
                    'HTTP_PR_STARTED',
                )

                if _uuid and _started:
                    response['PR-UUID'] = _uuid
                    response['PR-STARTED'] = _started

                if log_row:
                    for key, value in log_row.items():
                        if key not in self.exclude_attr_headers:
                            response[self._create_header(key)] = value

            except Exception as err:
                if settings.PRODUCTION_REQUEST_LOG_SERVER:
                    PRODUCTION_REQUEST_LOGGER.error(str(err))

    def _create_header(self, attr):
        return 'PR-S-{}'.format(attr.upper().replace("_", "-"))