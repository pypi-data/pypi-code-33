import click

from spell.cli.exceptions import api_client_exception_handler
from spell.cli.log import logger
from spell.cli.utils import prettify_time, tabulate_rows, HiddenOption


# display order of columns
COLUMNS = [
    "type",
    "name",
    "creator_name",
    "pretty_created_at",
    "pretty_updated_at",
]

# title lookup
TITLES = {
    "type": "TYPE",
    "name": "NAME",
    "creator_name": "CREATOR",
    "pretty_created_at": "CREATED",
    "pretty_updated_at": "UPDATED",
}


@click.command(name="workspaces",
               short_help="List workspaces")
@click.option("--raw", is_flag=True,
              help="Display output in raw format", cls=HiddenOption)
@click.pass_context
def workspaces(ctx, raw):
    """
    List all user workspaces

    A workspace is defined by the root commit of a git repository. Thus, the family of
    all Git commits that originate from the same root commit belong to the same workspace.
    Workspaces do not need to be managed or created -- they are created by the run command
    when necessary.
    """
    # grab the workspaces from the API
    workspaces = []
    client = ctx.obj["client"]
    with api_client_exception_handler():
        logger.info("Retrieving workspace information from Spell")
        workspaces = client.get_workspaces()

    # prepare objects for display
    for ws in workspaces:
        ws.type = "workspace"
        ws.id = str(ws.id)
        ws.creator_name = ws.creator.user_name
        ws.pretty_created_at = prettify_time(ws.created_at)
        ws.pretty_updated_at = prettify_time(ws.updated_at)

    # build the rows for tabulate
    sorted_rows = sorted(workspaces, key=lambda x: (x.type, x.updated_at), reverse=True)
    tabulate_rows(sorted_rows,
                  headers=[TITLES[col] for col in COLUMNS],
                  columns=COLUMNS,
                  raw=raw)
