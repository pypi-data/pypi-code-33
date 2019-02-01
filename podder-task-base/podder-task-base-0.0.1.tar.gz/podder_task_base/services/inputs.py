import json
import uuid
from typing import List, Dict
from podder_task_base import Context

'''
This service is only used for main.py.
'''
class InputsService(object):

    def __init__(self, context: Context) -> None:
        self.context = context

    def create(self) -> List:
        json_data = self.read_json()
        inputs = []
        for index, job_data in enumerate(json_data):
            inputs.append({
                "job_id": str(uuid.uuid4()),
                "job_data": job_data
            })
        return inputs

    def read_json(self) -> List:
        json_path = self.context.config.get('inputs')[0]
        with open(json_path) as f:
            return json.load(f)
