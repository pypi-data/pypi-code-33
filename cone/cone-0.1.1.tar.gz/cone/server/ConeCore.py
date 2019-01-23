import uuid

from time import sleep
from cone.ConeExit import ConeExit


class ConeCore(object):

    def __init__(self):
        self.tasks = []
        self.results = {}

    def add_task(self, task):
        id = str(uuid.uuid4())
        task['id'] = id
        self.tasks.append(task)
        return id

    def get_next_task(self):
        if len(self.tasks) == 0:
            return None
        else:
            return self.tasks.pop(0)

    def add_result(self, id, result):
        self.results[id] = result

    def get_result(self, id):
        return self.results.pop(id, None)

    def wait_for_result(self, id, timeout=10, delay=.2):
        result = self.get_result(id)
        time_passed = 0

        while result is None and time_passed < timeout:
            time_passed += delay
            sleep(delay)
            result = self.get_result(id)

        if result is None:
            raise ConeExit("request expired, make sure the cone-plugin is enabled")

        return result
