from invoke import task
from reliabilly.settings import Settings


COMMON_INSTALL = 'python reliabilly/setup.py install'
PIP_COMMAND = 'pip install -r requirements.txt'
PYLINT_LINT_CMD = 'pylint --disable=missing-docstring --output-format=parseable ' + Settings.LINT_MODULES
INVALID_SERVICE_MESSAGE = 'No service <{0}> found.'
DOCS_BUILD_CMD = 'ipecac --destination .'


@task
def services(_):
    """ Print a list of available services for operations
    like `inv start -s <service>`."""
    print('The following services are available for actions:')
    for service in Settings.SERVICES:
        print(service)


@task
def pylint(ctx):
    """ Run the pylint linter """
    ctx.run(PYLINT_LINT_CMD)


@task(post=[pylint])
def lint(_):
    """ Run all linters """
    print("Running linting...")


@task
def pip(ctx):
    """ Run pip install of requirements. """
    ctx.run(PIP_COMMAND)


@task
def docs(ctx):
    """ Build Swagger definition and move to app container """
    ctx.run(DOCS_BUILD_CMD)
