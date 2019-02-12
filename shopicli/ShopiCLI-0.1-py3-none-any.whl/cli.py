import json
import logging
import os
from functools import partial, update_wrapper

import click

import nicelog

from ._config import ConfigManager
from ._output import print_object
from .client import ShopifyClient

logger = logging.getLogger(__name__)

_home = os.path.expanduser('~')
xdg_config_home = (
    os.environ.get('XDG_CONFIG_HOME') or
    os.path.join(_home, '.config'))


cfg = ConfigManager(os.path.join(xdg_config_home, 'shopify'))


def with_shopify_client(f):
    """Decorator to pass client from context
    """

    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        conn_name = ctx.obj['CONNECTION_NAME']
        client = _get_store_client(conn_name) if conn_name else None
        logger.debug('Shopify client: {}'.format(client))
        return ctx.invoke(f, client, *args, **kwargs)

    return update_wrapper(new_func, f)


def _get_store_client(connection):
    credentials = cfg.get_connection(connection)
    client = ShopifyClient(
        store_name=credentials['store'],
        api_key=credentials['api_key'],
        password=credentials['password'])
    return client


def with_output_serializer(f):

    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        fmtname = ctx.obj['OUTPUT_FORMAT']
        serializer = partial(print_object, fmt=fmtname)
        return ctx.invoke(f, *args, **kwargs, print_object=serializer)

    return update_wrapper(new_func, f)


def autocomplete_connection_names(ctx, args, incomplete):
    connections = cfg.load_connections()
    return sorted(
        (name, '{0[store]} {0[api_key]}'.format(params))
        for name, params in connections.items())


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('conn_name', '--connection', '-c', default='default',
              autocompletion=autocomplete_connection_names)
@click.option('output_fmt', '--output-format', '-f', default=None)
@click.pass_context
def main(ctx, debug, conn_name, output_fmt):

    nicelog.setup_logging()
    log_level = logging.DEBUG if debug else logging.INFO
    logging.getLogger().setLevel(log_level)

    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    ctx.obj['CONNECTION_NAME'] = conn_name
    ctx.obj['OUTPUT_FORMAT'] = output_fmt


@main.group('connection')
def grp_connection():
    """Manage connections to Shopify stores"""
    pass


def store_name_info(ctx, param, value):
    print(
        'Head to https://{}.myshopify.com/admin/apps/private if you need '
        'to create a new API key.'
        .format(value))
    return value


@grp_connection.command('create')
@click.option('--name', '-n', prompt='Name this connection',
              help='Connection name, used to refer to this connection',
              default='default')
@click.option('--store', '-s', prompt='Store name', callback=store_name_info,
              help='Shopify store name')
@click.option('--api-key', prompt='API key', help='Shopify API key')
@click.option('--password', prompt='API key password', hide_input=True,
              help='Shopify API password')
def cmd_connection_create(name, store, api_key, password):
    """Create a new connection"""
    cfg.create_connection(name, {
        'store': store,
        'api_key': api_key,
        'password': password,
    })


@grp_connection.command('list')
def cmd_connection_list():
    """List available connections"""
    connections = cfg.load_connections()
    for name, params in sorted(connections.items()):
        click.echo(
            '\x1b[1;32m{name}:\x1b[0m \x1b[1m{p[store]}\x1b[0m {p[api_key]}'
            .format(name=name, p=params))


@grp_connection.command('delete')
@click.argument('name')
def cmd_connection_delete(name):
    """Delete a connection"""
    cfg.delete_connection(name)


@main.group('products')
def grp_products():
    """Manage products"""
    pass


@grp_products.command('get')
@click.argument('product_id')
@with_shopify_client
def cmd_products_get(client, product_id):
    product = client.get_product_by_id(product_id)
    print_object(product)


@grp_products.command('list')
@with_shopify_client
@with_output_serializer
def cmd_products_list(client, print_object):
    products = client.list_all_products()
    print_object(products)


@grp_products.command('export')
@with_shopify_client
@with_output_serializer
def cmd_products_export(client, print_object):
    products = client.list_all_products()
    print_object({'products': products})


@main.command('import')
@click.argument('input_file', type=click.File('rb'), default='-')
@click.option('--info', default=False, is_flag=True,
              help='Only show information about the data file')
@with_shopify_client
@with_output_serializer
def cmd_import(client, input_file, info, print_object):
    """Import data to a store"""

    data = json.load(input_file)

    if not isinstance(data, dict):
        raise TypeError('Invalid data file (expected JSON object)')

    if 'products' in data:
        click.echo('\x1b[1;31mProducts:\x1b[0m')
        width, height = click.get_terminal_size()

        indent = '    - '
        ellipsis = '...'
        max_width = width - len(indent)

        for product in data['products']:
            text = json.dumps(product)
            if len(text) > max_width:
                text = text[:max_width - len(ellipsis) - 1] + ellipsis
            click.echo('{}{}'.format(indent, text))


if __name__ == '__main__':
    main()
