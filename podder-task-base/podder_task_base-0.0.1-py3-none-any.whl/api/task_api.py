import json

import pipeline_framework_pb2
import pipeline_framework_pb2_grpc
from app import Task
from podder_task_base import Context, settings


class PocBaseApi(pipeline_framework_pb2_grpc.PocBaseApiServicer):
    def execute(self, request, _context):
        settings.init()
        dag_id = request.dag_id
        context = Context(dag_id)
        inputs = self._convert_to_input_data(request)
        outputs = Task(context).execute(inputs)
        task_response = self._convert_to_task_response(dag_id, outputs)
        return task_response

    def _convert_to_input_data(self, request):
        inputs = []
        for result in request.results:
            inputs.append({
                'job_id': result.job_id,
                'job_data': json.loads(result.job_data)
            })
        return inputs

    def _convert_to_task_response(self, dag_id: str, outputs):
        task_response = pipeline_framework_pb2.TaskResponse()
        task_response.dag_id = dag_id
        for output in outputs:
            task_response.results.add(job_id=output['job_id'], job_data=json.dumps(output['job_data']))
        return task_response
