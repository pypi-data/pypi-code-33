import argparse
import pathlib
import multiprocessing

from irori import context, executors
from irori.depend import Dependencies


def start(target, recipes, finder, dependencies=None, arguments=None):
    parser = argparse.ArgumentParser(description='Build tool')
    parser.add_argument('--debug', '-d', help='run as debug mode', action='store_true')
    parser.add_argument('--release', '-r', help='run as release mode (default)', action='store_true')
    parser.add_argument(
        '--object', '--obj', '--object-directory', help='temporary object output directory (default obj)',
        default='obj')
    parser.add_argument('--no-concurrency', help='disable concurrency', action='store_true')
    parser.add_argument(
        '--concurrency',
        help='concurrency level > 0 (default {})'.format(multiprocessing.cpu_count()),
        type=int, default=multiprocessing.cpu_count())

    handler = None

    if dependencies is None:
        dependencies = Dependencies()

    if arguments is not None:
        arguments(parser)
    recipe_entries = recipes()

    sub = parser.add_subparsers()
    subparsers = {recipe: sub.add_parser(recipe) for recipe in recipe_entries.keys()}
    [parser.set_defaults(handler=recipe_entries[name]) for name, parser in subparsers.items()]

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        handler = args.handler

    if handler is None:
        parser.print_help()
        exit(1)

    build_context = context.BuildContext(
        pathlib.Path(args.object),
        target, context.Mode.debug if args.debug else context.Mode.release, dependencies, args)
    rule = handler(build_context)

    dependencies = finder(build_context)

    core = args.concurrency
    if args.no_concurrency:
        core = 1

    executor = executors.Executor(core)

    rule.initialize(build_context)

    runtime_context = context.RuntimeContext([pathlib.Path(dep) for dep in dependencies])

    rule.execute(runtime_context, executor)
    executor.wait_all()
