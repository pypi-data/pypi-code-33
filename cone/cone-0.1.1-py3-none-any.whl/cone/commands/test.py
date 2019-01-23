from cone import project
from cone.ConeExit import ConeExit


def test(cone_server):
    configuration = project.get_configuration()
    project_data = project.get_project_content(configuration)

    task = {
        "task_name": "test",
        "configuration": configuration,
        "project": project_data
    }

    id = cone_server.add_task(task)
    cone_server.start()

    result = cone_server.wait_for_result(id)

    return ConeExit.fromResult(result)
