import logging

import time

from .helpers import SerenyticsException, make_request
from . import settings

logger = logging.getLogger(__name__)


class Task(object):
    """
    Serenytics task: represents an asynchronous job running in Serenytics backend.
    """

    def __init__(self, task_id, description, headers):
        self._task_id = task_id
        self._description = description
        self._headers = headers

        self._is_finished = False
        self._result = None
        self._errors = None

    def wait(self, time_before_retry_s=1):
        """
        Wait for task to be finished
        """
        if self._is_finished:
            return

        logger.info('Waiting for task "{description}" (id={id}) to be finished, polling every {polling} s'
                    .format(description=self._description, id=self._task_id, polling=time_before_retry_s))
        while True:
            still_running = self._is_pending()
            if not still_running:
                self._is_finished = True
                break
            time.sleep(time_before_retry_s)

    @property
    def result(self):
        if not self._is_finished:
            raise TaskStillRunning()

        return self._result

    def raise_on_error(self):
        if not self._is_finished:
            raise TaskStillRunning()

        if self._errors is not None:
            raise SerenyticsException(self._errors[0])

    def _is_pending(self):
        task_url = settings.SERENYTICS_API_DOMAIN + '/api/task/' + self._task_id
        data = make_request('get', task_url, headers=self._headers, log_request=False).json()

        if data['status'] == 'pending':
            return True

        if 'errors' in data:
            self._errors = data.get('errors')
        else:
            self._result = data

        return False


class TaskStillRunning(SerenyticsException):
    def __init__(self):
        super(TaskStillRunning, self).__init__('Task is still running. You should call task.wait() before asking'
                                               ' for result')
