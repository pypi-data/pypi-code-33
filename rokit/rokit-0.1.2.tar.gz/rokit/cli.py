from __future__ import absolute_import
import click
import requests
import sys
from .__version__ import __version__
from .util import pass_tag, fail_tag, highlight

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('version: %s' % __version__)
    ctx.exit()


def highlight_matched_url(origin_url, expect_url):
    return highlight(origin_url) if origin_url == expect_url else origin_url


def parse_redirect_chain(response):
    return list(map(lambda item: item.headers['Location'], response.history))


def highlight_redirect_chain(redirect_chain, expect_url):
    return list(map(lambda item: highlight_matched_url(item, expect_url), redirect_chain))


def print_redirect_chain(redirect_chain):
    click.echo('Redirect %s time(s): %s ' %
               (len(redirect_chain)-1, ' -> '.join(redirect_chain)))


def argument_valid(origin_url, expect_url):
    return origin_url is not None or expect_url is not None

@click.command()
@click.option('--version', '-v',
              is_flag=True,
              callback=print_version,
              expose_value=False,
              is_eager=True,
              help='Show the version of rokit')
@click.argument('origin_url', required=False)
@click.argument('expect_url', required=False)
@click.pass_context
def cli(ctx, origin_url, expect_url):
    if argument_valid(origin_url, expect_url):
        cli_url(origin_url, expect_url)
    else:
        click.echo(ctx.get_help())


def cli_url(origin_url, expect_url):
    response = requests.get(origin_url)
    redirect_chain = [
        origin_url] + highlight_redirect_chain(parse_redirect_chain(response), expect_url)
    print_redirect_chain(redirect_chain)
    if expect_url != None:
        url_found = highlight(expect_url) in redirect_chain
        result_msg = ' Request to %s will %s redirect to %s' % (
            origin_url, '' if url_found else 'not', expect_url)
        if url_found:
            click.echo(pass_tag(result_msg))
            sys.exit()
        else:
            click.echo(fail_tag(result_msg))
            sys.exit(1)
