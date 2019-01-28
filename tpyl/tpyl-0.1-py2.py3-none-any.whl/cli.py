#!/usr/bin/env python

import click

import tpyl


@click.command(help='Renders a template')
@click.argument('path', default='-', type=str)
@click.option('--var', '-v', 'var', type=str, multiple=True,
              help='Variable in the form KEY=VALUE')
@click.option('--context', '-c', 'context', type=str, multiple=True,
              help='Path to a context file')
@click.option('--filter', '-f', 'filters', type=str, multiple=True,
              help='Path to a filters file')
@click.option('--output', '-o', 'output', type=str,
              help='Path of a file which will be written with the result')
@click.option('--no-env', 'noenv', type=str, is_flag=True, flag_value=False,
              help='Prevent environment variables to be passed to the template')
def cli(path, var, context, filters, output, noenv):
    main(path, var, context, filters, output, noenv)
    exit(0)


def main(path, var=None, context=None, filters=None, output=None, noenv=False):
    ctx = tpyl.load_context(var=var or (), context=context or (), env=noenv)
    tpl = tpyl.render_template(path, ctx, filters=filters, stream=click.get_text_stream('stdin'))
    tpyl.write_render(tpl, output, stream=click.get_text_stream('stdout'))
