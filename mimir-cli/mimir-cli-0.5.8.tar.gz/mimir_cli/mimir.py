"""
the main mimir cli click module
"""
import click
from mimir_cli.globals import __version__
from mimir_cli.strings import (
    AUTH_SUCCESS,
    EMAIL_HELP,
    EMAIL_PROMPT,
    ERR_INVALID_CRED,
    ERR_NOT_AUTH,
    LOGOUT_SUCCESS,
    PW_HELP,
)
from mimir_cli.utils.auth import login_to_mimir, logout_of_mimir, read_credentials
from mimir_cli.utils.projects import (
    get_projects_list,
    prompt_for_project,
    print_projects,
)
from mimir_cli.utils.state import State, debug
from mimir_cli.utils.submit import submit_to_mimir


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option("-v", "--verbose", is_flag=True, default=False, hidden=True)
def cli(ctx, verbose):
    """Mimir Classroom CLI"""
    state = ctx.ensure_object(State)
    state.verbose = verbose
    debug("[+] verbose mode enabled")


@cli.command()
def version():
    """print version info"""
    click.echo("mimir-cli version {version}".format(version=__version__))


@cli.command()
@click.option("-e", "--email", help=EMAIL_HELP, prompt=EMAIL_PROMPT, metavar="<email>")
@click.option(
    "-p", "--password", help=PW_HELP, prompt=True, hide_input=True, metavar="<string>"
)
def login(email, password):
    """log in to Mimir Classroom"""
    logged_in = login_to_mimir(email, password)
    if logged_in:
        click.echo(AUTH_SUCCESS)
        return True
    click.echo(ERR_INVALID_CRED)
    return False


@cli.command()
def logout():
    """log out of Mimir Classroom"""
    logout_of_mimir()
    click.echo(LOGOUT_SUCCESS)


@cli.group()
def project():
    """project related commands"""
    pass


@project.command()
@click.option(
    "--path",
    help="the file or directory to submit",
    prompt=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
    metavar="<file path>",
)
@click.option(
    "--project-id",
    help="the project id on Mimir Classroom",
    type=click.UUID,
    metavar="<uuid>",
)
@click.option(
    "--on-behalf-of",
    help="email to submit on behalf of (instructor only)",
    type=str,
    metavar="<email>",
)
@click.option(
    "--custom-penalty",
    help="custom penalty for the submission (instructor only)",
    type=float,
    default=0.0,
    show_default=True,
    metavar="<float>",
)
def submit(path, project_id, on_behalf_of, custom_penalty):
    """
    submit files to a project on Mimir Classroom.

    \b
    if you are logged in as an instructor,
    you can also submit on behalf of another user,
    denoted by email, optionally adding a custom penalty
    """
    credentials = read_credentials()
    if credentials and "user_session_id" in credentials:
        if not project_id:
            projects = get_projects_list(credentials)
            selected_project = prompt_for_project(projects)
            project_id = selected_project["id"]
        submit_to_mimir(
            path,
            project_id,
            credentials,
            on_behalf_of=on_behalf_of,
            custom_penalty=custom_penalty,
        )
    else:
        click.echo(ERR_NOT_AUTH)


@project.command()
@click.option(
    "-l",
    "--limit",
    default=20,
    help="maximum number of projects to show",
    show_default=True,
    metavar="<int>",
)
def ls(limit):
    """list open projects for this account on Mimir Classroom"""
    credentials = read_credentials()
    if credentials and "user_session_id" in credentials:
        projects = get_projects_list(credentials)[:limit]
        print_projects(projects)
    else:
        click.echo(ERR_NOT_AUTH)


if __name__ == "__main__":
    cli()  # noqa
