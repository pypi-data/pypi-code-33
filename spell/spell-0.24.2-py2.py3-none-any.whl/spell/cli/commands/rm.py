import sys

import click

from spell.cli.exceptions import api_client_exception_handler, ExitException
from spell.cli.log import logger


@click.command(name="rm",
               short_help="Specify one or more resources to delete. These can be [run_id] or uploads/[directory]")
@click.argument("resources", required=True, nargs=-1)
@click.pass_context
def rm(ctx, resources):
    """
    Remove one or more resources.
    To remove a finished or failed run simply use its RUN_ID.
    To remove a resource use uploads/DIRECTORY.

    The removed runs will no longer show up in `ps`. The outputs of removed runs
    and removed uploads will no longer appear in `ls` or be mountable on
    another run with `--mount`.
    """
    client = ctx.obj["client"]

    logger.info("Deleting resource={}".format(resources))
    exit_code = 0
    for resource in resources:
        try:
            with api_client_exception_handler():
                if resource.startswith("uploads/"):
                    client.remove_dataset(resource[8:])
                elif resource.startswith("runs/"):
                    client.remove_run(resource[5:])
                else:
                    client.remove_run(resource)
        except ExitException as e:
            exit_code = 1
            e.show()
    sys.exit(exit_code)
