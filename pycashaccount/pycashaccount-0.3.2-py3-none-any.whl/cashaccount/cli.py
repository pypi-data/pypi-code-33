import click

from . import electron_markdown as ecmd
from . import opreturn as ophex
from . import KeyHashInfo, ScriptHashInfo, PaymentCodeInfo
from . import Registration


FMT_OPRETURN = 'opreturn'
FMT_EC_MARKDOWN = 'electron-markdown'
FMTS = [
    FMT_OPRETURN,
    FMT_EC_MARKDOWN,
]


@click.group()
def run():
    pass


@run.command()
@click.argument('name')
@click.argument('cash_or_legacy_address')
@click.option('-f', '--format', 'fmt', type=click.Choice(FMTS))
def keyhash(name, cash_or_legacy_address, fmt):
    try:
        info = KeyHashInfo(cash_or_legacy_address)
    except ValueError as e:
        raise click.exceptions.BadParameter('Unable to create payment info: {}'.format(e))

    try:
        r = Registration(name, info)
    except ValueError as e:
        raise click.exceptions.BadParameter('Unable to create registration: {}'.format(e))

    s = _format(r, fmt)
    click.echo(s)


@run.command()
@click.argument('name')
@click.argument('cash_or_legacy_address', type=click.types.STRING)
@click.option('-f', '--format', 'fmt', type=click.Choice(FMTS))
def scripthash(name, cash_or_legacy_address, fmt):
    try:
        info = ScriptHashInfo(cash_or_legacy_address)
    except ValueError as e:
        raise click.exceptions.BadParameter('Unable to create payment info: {}'.format(e))

    try:
        r = Registration(name, info)
    except ValueError as e:
        raise click.exceptions.BadParameter('Unable to create registration: {}'.format(e))

    s = _format(r, fmt)
    click.echo(s)


SRC_PAYMENT_CODE = 'from-code'
SRC_XPUB = 'from-xpub'
SRCS = [
    SRC_PAYMENT_CODE,
    SRC_XPUB,
]


@run.command()
@click.argument('name')
@click.argument('source-type', type=click.Choice(SRCS))
@click.argument('source', type=click.types.STRING)
@click.option('-f', '--format', 'fmt', type=click.Choice(FMTS))
def paymentcode(name, source_type, source, fmt):
    maker = {
        SRC_PAYMENT_CODE: PaymentCodeInfo,
        SRC_XPUB: PaymentCodeInfo.from_xpub,
    }[source_type]
    try:
        info = maker(source)
    except ValueError as e:
        raise click.exceptions.BadParameter('Unable to create payment info: {}'.format(e))

    try:
        r = Registration(name, info)
    except ValueError as e:
        raise click.exceptions.BadParameter('Unable to create registration: {}'.format(e))

    s = _format(r, fmt)
    click.echo(s)


def _format(registration, fmt):
    formatter = {
        FMT_OPRETURN:    ophex,
        FMT_EC_MARKDOWN: ecmd,
        None:            str,
    }[fmt]
    return formatter(registration)
