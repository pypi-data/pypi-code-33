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
        log_row = self._log_request(request)
        self._add_response_headers(request, response, log_row)

        return response

    def process_exception(self, request, exception):
        self._log_request(request)

    def _start_log_request(self, request):
        """
        Начинает процесс логирования запроса
        """
        if settings.PRODUCTION_REQUEST:
            request_uuid = str(uuid.uuid4())[-12:]

            thread_data = get_thread_data()
            thread_data.production_request_uuid = request_uuid

            request.started_at = datetime.now()
            request.production_request_uuid = request_uuid
            request.production_request_rss = self._get_memory_rss()

    def _get_memory_rss(self):
        """Возвращает значени Resident Set Size памяти процесса"""
        return float(Process(os.getpid()).memory_info().rss)

    def _get_rss_diff(self, rss_begin, rss_end):
        """Возвращает разницу размера памяти в МБ"""
        return (rss_end - rss_begin) / 1024 / 1024 / 8

    def _log_request(self, request):
        """Логирует параметры запроса и результаты обработки"""
        row = None
        if settings.PRODUCTION_REQUEST:
            try:
                _uuid = request.META.get(
                    'HTTP_PR_UUID',
                    ''
                )
                process_request_time = ms_from_timedelta(
                    datetime.now() - request.started_at
                )
                process_sql_time = connections['default'].sql_time.pop(
                    request.production_request_uuid, float())

                sql_count = connections['default'].sql_count.pop(
                    request.production_request_uuid, 0)

                rss_diff = self._get_rss_diff(
                    request.production_request_rss, self._get_memory_rss())

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
                    'rss': '{:.2f}'.format(rss_diff)
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

            return row

    def _create_header(self, attr):
        return 'PR-S-{}'.format(attr.upper().replace("_", "-"))

    def _add_response_headers(self, request, response, log_row):
        if settings.PRODUCTION_REQUEST_LOG_CLIENT:
            try:
                _uuid = request.META.get(
                    'HTTP_PR_UUID',
                )
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