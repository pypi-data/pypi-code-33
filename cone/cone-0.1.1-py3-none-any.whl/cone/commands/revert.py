from cone.project import get_project_content, get_configuration
from cone.ConeExit import ConeExit


def revert(cone_server):
    task = {
        "task_name": "revert"
    }

    id = cone_server.add_task(task)
    cone_server.start()

    result = cone_server.wait_for_result(id)

    return ConeExit.fromResult(result)
