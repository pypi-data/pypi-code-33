from cone import project
from cone.ConeExit import ConeExit


def deploy(cone_server, include_tests, obfuscate):
    configuration = project.get_configuration()
    project_data = project.get_project_content(configuration)

    if obfuscate:
        pass

    task = {
        "task_name": "deploy",
        "configuration": configuration,
        "project": project_data,
        "include_tests": include_tests
    }

    id = cone_server.add_task(task)
    cone_server.start()

    result = cone_server.wait_for_result(id)

    return ConeExit.fromResult(result)
