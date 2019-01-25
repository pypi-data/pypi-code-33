from datetime import datetime

import click
import crayons
import tweakers
from tabulate import tabulate

from . import __version__, config, utils


def format_date(dt):
    if dt.date() == datetime.today().date():
        return dt.strftime("%H:%M")
    elif dt.year == datetime.today().year:
        return dt.strftime("%d-%m")
    else:
        return dt.strftime("%d-%m-%Y")


def confirm_overwrite_existing_login():
    if utils.cookies_exist():
        confirmed = click.confirm(
            "You are already logged in. Would you like to login to a different account?"
        )
        if confirmed:
            config.stored_cookies_path.unlink()
            click.echo("Existing login deleted.")
        else:
            raise SystemExit


def print_comment(comment):
    """Pretty print a comment"""
    print(
        crayons.yellow((comment.date.strftime("%H:%M"))),
        crayons.green(comment.user.name),
        crayons.blue(comment.url),
    )
    print(comment.text, "\n")


def choose_topic(topics):
    """Return chosen topic from a printed list of topics

    Args:
        topics (list): List of Topic objects

    Returns:
        topic (Topic): Chosen topic
    """
    table = []
    for i, t in enumerate(topics):
        row = [i + 1, t.title, format_date(t.last_reply)]
        table.append(row)
    print("\n", tabulate(table, headers=["#", "Titel", "Laatste reactie"]))

    choice = click.prompt(f"\nChoose a topic to stream (1-{len(topics)})", type=int)
    return topics[choice - 1]


@click.group()
@click.version_option(version=__version__)
@click.option("--last", default=3, help="Number of previous comments to show.")
@click.pass_context
def cli(ctx, last):
    ctx.ensure_object(dict)
    ctx.obj["last"] = last

    try:
        utils.load_persistent_cookies()
    except FileNotFoundError:
        pass


@cli.command(name="stream", help="Stream from a specific url.")
@click.argument("url")
@click.pass_context
def stream(ctx, url):
    topic = tweakers.gathering.Topic(url=url)
    for comment in topic.comment_stream(last=ctx.obj["last"]):
        print_comment(comment)


@cli.command(name="list", help="Choose from a list of active topics.")
@click.option("-n", default=20, help="Number of topics to show.")
@click.pass_context
def list_active(ctx, n):
    topics = tweakers.gathering.active_topics()[:n]

    topic = choose_topic(topics)
    for comment in topic.comment_stream(last=ctx.obj["last"]):
        print_comment(comment)


@cli.command(name="search", help="Search for a specific topic.")
@click.argument("query", nargs=-1)
@click.option("-n", default=10, help="Number of results to show.")
@click.pass_context
def search(ctx, query, n):
    query = " ".join(query)
    topics = tweakers.gathering.search(query)

    if len(topics) == 0:
        click.echo("No topics found!")
        raise SystemExit

    topic = choose_topic(topics)
    for comment in topic.comment_stream(last=ctx.obj["last"]):
        print_comment(comment)


@cli.command(name="login", help="Login to tweakers.net.")
def login():
    confirm_overwrite_existing_login()

    username = click.prompt("Username")
    password = click.prompt("Password", hide_input=True)

    tweakers.utils.login(username=username, password=password)
    utils.store_persistent_cookies()
    click.echo("Login successful!")


@cli.command(name="bookmarks", help="Choose from a list of bookmarks.")
@click.pass_context
def bookmarks(ctx):
    topics = tweakers.gathering.bookmarks()

    if len(topics) == 0:
        click.echo("No topics found!")
        raise SystemExit

    topic = choose_topic(topics)
    for comment in topic.comment_stream(last=ctx.obj["last"]):
        print_comment(comment)


if __name__ == "__main__":
    cli(obj={})
