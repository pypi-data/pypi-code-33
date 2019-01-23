from invoke import Collection, task
from reliabilly.tasks import docker, build, data, tests, process, deploy, debug, chat, k8s, publish
from reliabilly.scaffold.generator import scaffold_up_service
from reliabilly.settings import Constants, Settings


ns = Collection()  # pylint: disable=invalid-name
ns.add_collection(Collection.from_module(docker))
ns.add_collection(Collection.from_module(process))
ns.add_collection(Collection.from_module(build))
ns.add_collection(Collection.from_module(deploy))
ns.add_collection(Collection.from_module(data))
ns.add_collection(Collection.from_module(tests))
ns.add_collection(Collection.from_module(debug))
ns.add_collection(Collection.from_module(chat))
ns.add_collection(Collection.from_module(k8s))


def get_collections():
    collections = list(ns.collections)
    collections.sort()
    return collections


@task(default=True, pre=[build.lint, tests.test], aliases=['build'])
def default(_):
    """ Default invoke task which should be run often during development. """
    pass


@task(pre=[build.lint, tests.test, tests.integration])
def rebuild(_):
    """ Run lint, unit tests, purge, build, and integration tests. """
    pass


@task(aliases=['generate', 'gen'])
def scaffold(_, service):
    """ Scaffold up a new service. """
    next_priority = Constants.STARTING_PRIORITY + len(Settings.SERVICES)
    scaffold_up_service(service, next_priority)


@task
def assume(_, token):
    """ Assume a role and print out the access tokens for the credentials"""
    debug.assume(token)


@task(optional=['namespace'], aliases=['list'])
def ls(_):  # pylint: disable=invalid-name
    """ List which tasks exist for each namespace. """
    print('The following tasks exist by namespace...')
    print('-' * 100)
    collections = get_collections()
    for collection in collections:
        task_list = list(ns.collections[collection].tasks)
        task_list.sort()
        printed_tasks = ', '.join(task_list)
        print(f'{collection} = {printed_tasks}')


@task(aliases=['ns'])
def namespace(_):
    """ List which namespaces exist. """
    print('The following namespaces exist...')
    print('-' * 100)
    collections = get_collections()
    print('\n'.join(collections))


# The following tasks are runnable from the top level without needed to prepend namespace.
ns.add_task(ls)
ns.add_task(namespace)
ns.add_task(default)
ns.add_task(rebuild)
ns.add_task(assume)
ns.add_task(tests.test)
ns.add_task(build.lint)
ns.add_task(build.pip)
ns.add_task(docker.up)
ns.add_task(docker.down)
ns.add_task(docker.images)
ns.add_task(docker.sh)
ns.add_task(docker.logs)
ns.add_task(docker.tail)
ns.add_task(docker.ps)
ns.add_task(docker.psa)
ns.add_task(docker.rm)
ns.add_task(docker.rmi)
ns.add_task(docker.stop)
ns.add_task(docker.purge)
ns.add_task(docker.raw)
ns.add_task(docker.clean)
ns.add_task(tests.integration)
ns.add_task(tests.int_test)
ns.add_task(tests.start)
ns.add_task(build.services)
ns.add_task(process.pr)
ns.add_task(scaffold)
ns.add_task(process.check_service_versions)
ns.add_task(deploy.terraform_deploy)
ns.add_task(process.wu)
ns.add_task(process.wu_me)
ns.add_task(process.add_secret)
ns.add_task(process.update_secret)
ns.add_task(process.delete_secret)
ns.add_task(process.update_service_secrets)
ns.add_task(process.encrypt_secrets)
ns.add_task(process.decrypt_secrets)
ns.add_task(chat.send_pipeline_message)
ns.add_task(chat.populate_pull_info)
ns.add_task(publish.publish)
