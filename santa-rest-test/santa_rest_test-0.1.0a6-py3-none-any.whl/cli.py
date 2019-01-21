# -*- coding: utf-8 -*-

"""Console script for apitest."""
import sys
import asyncio
import aiohttp
import json
from functools import partial

import yaml

from jq import jq

import click

from santa.loader import load_context, load_suite
from santa import init


class FakeCookieJar:
    def update_cookies(self, *args, **kwargs):
        pass

    def filter_cookies(self, *args, **kwargs):
        return []


async def run(context, suite, extra_vars, debug, output):
    # init context
    context = await load_context(context)
    for k, v in extra_vars:
        context.bind(k, v, create=True)
    if output == "stdout":
        out = sys.stdout
    else:
        out = sys.stderr
    context["_out"] = out
    context["_debug"] = debug
    context["_suite_done"] = []

    # load plugins
    init()

    # run the suite
    suite = await load_suite(suite)
    async with aiohttp.ClientSession() as sess:
        sess._cookie_jar = FakeCookieJar()
        context["_http_session"] = sess
        result = await suite(context)

    # format results
    result = result.as_dict()
    out.write(format_summary(result) + "\n")
    if output == "json":
        print(json.dumps(result))
    if output == 'yaml':
        print(yaml.dump(result))
    if not result.get("success", False):
        sys.exit(1)


def format_summary(result):
    tests = jq(
        '[..|objects|select(.type=="test")]'
    ).transform(result)
    skipped = jq(
        '[..|objects|select(.type=="test")|select(.skipped)]'
    ).transform(result)
    failed = jq(
        '[..|objects|select(.type=="test")|select(.success==false)]'
    ).transform(result)
    success = jq(
        '[..|objects|select(.type=="test")|select(.success==true)]'
    ).transform(result)
    output = "\nSummary\n"
    summary = "tests: %s    success: %s    skipped: %s    failed: %s\n" % (
        len(tests), len(success), len(skipped), len(failed))
    output += "*" * len(summary) + "\n"
    output += summary
    output += "*" * len(summary) + "\n"
    return output


def parse_extra(extra_vars):
    return [extra.split("=", 1) for extra in extra_vars]


@click.group()
def main():
    pass


@main.command()
@click.argument("context")
@click.argument("suite")
@click.option("-e", "--extra-var",
              multiple=True,
              metavar="'var.nested=val'",
              help="Set a context value. Multiple --extra-var can be passed.")
@click.option("-d", "--debug",
              is_flag=True, help="Toggle debug output for all tasks.")
@click.option("-o", "--output",
              type=click.Choice(["-", "json", "yaml"]),
              default="-",
              show_default=True,
              help="Output format. "
              "If not '-' (stdout), all debug output is dumped in stderr")
def test(context, suite, extra_var, debug, output):
    """Run the given SUITE, starting with the given CONTEXT"""
    extra = parse_extra(extra_var)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(context, suite, extra, debug, output))
    return 0


@main.group("list")
def list_():
    """List available objects"""
    pass


@list_.command("tasks")
def list_tasks():
    "List available tasks"
    init()
    from santa.task import TaskBase
    for name, task in sorted(
            [(n, t) for (n, t) in TaskBase.registry.items()
                if not t.__abstract__]):
        doc = task.__doc__
        if doc:
            doc = doc.strip().splitlines()[0]
        else:
            doc = ""
        print("%s: %s" % (name, doc))


@list_.command("context-processors")
def list_context_processors():
    "List available context processors"
    init()
    from santa.context_processor import ContextProcessorBase
    for name, task in sorted(
            [(n, t) for (n, t) in ContextProcessorBase.registry.items()
                if not t.__abstract__]):
        doc = task.__doc__
        if doc:
            doc = doc.strip().splitlines()[0]
        else:
            doc = ""
        print("%s: %s" % (name, doc))


@list_.command("validators")
def list_validators():
    "List available validators"
    init()
    from santa.validator import ValidatorBase
    for name, task in sorted(
            [(n, t) for (n, t) in ValidatorBase.registry.items()
                if not t.__abstract__]):
        doc = task.__doc__
        if doc:
            doc = doc.strip().splitlines()[0]
        else:
            doc = ""
        print("%s: %s" % (name, doc))


@list_.command("extractors")
def list_extractors():
    "List available extractors"
    init()
    from santa.extractor import ExtractorBase
    for name, task in sorted(
            [(n, t) for (n, t) in ExtractorBase.registry.items()
                if not t.__abstract__]):
        doc = task.__doc__
        if doc:
            doc = doc.strip().splitlines()[0]
        else:
            doc = ""
        print("%s: %s" % (name, doc))


@main.group("scaffold")
@click.option("--with-help", is_flag=True, help="Output help as yaml comments")
def scaffold(with_help=False):
    """Scaffold yaml declaration of objects"""
    pass


class ScaffoldTask(click.MultiCommand):

    def list_commands(self, ctx):
        init()
        from santa.task import TaskBase
        return sorted(TaskBase.registry.keys())

    def get_command(self, ctx, name):
        init()
        from santa.task import TaskBase
        return click.Command(
                name,
                callback=partial(
                    TaskBase.registry[name].scaffold,
                    comments=ctx.parent.params["with_help"]
                )
            )


# scaffold.add_command(ScaffoldTask(name="tasks"))

@scaffold.command("tasks", cls=ScaffoldTask)
def sctasks():
    pass

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
