import click

from ..constants import DEFAULT_DB_PATH, USER_HOME
from . import utils


@click.group()
@click.option("--db", default=DEFAULT_DB_PATH, type=click.Path(),
              help=f"path to db (default: {DEFAULT_DB_PATH})".replace(USER_HOME, "~"))
@click.pass_context
def cybele(ctx, db):
    """
    command line password manager
    """
    ctx.obj = {
        "db_path": db,
    }


@cybele.command()
@click.option("--db", default=DEFAULT_DB_PATH, type=click.Path(),
              help=f"path to db (default: {DEFAULT_DB_PATH})".replace(USER_HOME, "~"))
def init(db):
    """initialize a new db"""
    utils.create_db(db)


@cybele.command()
@click.option("-g", "--grep", default="", help="filter entries matching string")
@click.pass_context
def ls(ctx, grep):
    """list all entries"""
    db_path = ctx.obj["db_path"]
    db = utils.load_db(db_path)
    if not db.entries:
        utils.echo_exit("No entries yet. See 'cybele add --help'", 0)

    headers = [["ENTRY", "USERNAME", "PASSPHRASE"]]
    data = headers + [
        [entry_name, entry["username"], "*" * 10]
        for entry_name, entry in db.entries.items()
        if grep in entry_name or grep in entry["username"]
    ]
    table = utils.Table(data, inner_heading_row_border=True)
    click.echo(f"{table}")


@cybele.command()
@click.argument("entry_name")
@click.pass_context
def add(ctx, entry_name):
    """add new entry"""
    db_path = ctx.obj["db_path"]
    db = utils.load_db(db_path)
    entry = utils.ask_full_infos()
    db.add(entry_name=entry_name, entry=entry)
    db.dump(ctx.obj["db_path"])


@cybele.command()
@click.argument("entry_name")
@click.pass_context
def edit(ctx, entry_name):
    """edit an entry"""
    db_path = ctx.obj["db_path"]
    db = utils.load_db(db_path)
    entry = utils.ask_full_infos()
    db.edit(entry_name=entry_name, updates=entry)
    db.dump(ctx.obj["db_path"])


@cybele.command()
@click.argument("entry_name")
@click.pass_context
def rm(ctx, entry_name):
    """removes an entry"""
    db_path = ctx.obj["db_path"]
    db = utils.load_db(db_path)
    confirmation = utils.confirm_yes_no(f"Are you sure you want to delete '{entry_name}' ?")
    if confirmation:
        db.delete(entry_name)
    db.dump(ctx.obj["db_path"])


@cybele.command()
@click.argument("entry_name")
@click.option('-u', "--username", is_flag=True, help="copy entry username instead of passphrase")
@click.pass_context
def cp(ctx, entry_name, username):
    """copy passphrase (or username) to clipboard"""
    db_path = ctx.obj["db_path"]
    db = utils.load_db(db_path)
    if username:
        db.clip_username(entry_name)
    else:
        db.clip_passphrase(entry_name)
