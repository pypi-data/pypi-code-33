import argparse
import os
import sys
from functools import partial

from ..util import rwalk, run, logger
from .config import init_config, read_config, get_repos
from .vcs import clone, pull, push, set_remote, sync


DEFAULT_CFG_FILE = "mirror.cfg"


def _add_arg_repo(parser):
    parser.add_argument(
        "-r", "--repo", help='repository to act on, default: "all"', default="all"
    )


def _add_arg_branch(parser):
    parser.add_argument(
        "-b",
        "--branch",
        help='branch to act on, default: "default"',
        default="default",
    )


def get_parser():
    parser = argparse.ArgumentParser(
        prog="fluidmirror OR fm",
        description=(
            "A tool to handle multiple repositories. "
            "Works on a specific / all configured repositories (default)"
        ),
    )
    parser.add_argument(
        "-c", "--cfg", help="config file", default=DEFAULT_CFG_FILE
    )
    subparsers = parser.add_subparsers(title="basic commands", metavar="")

    parser_list = subparsers.add_parser("init", help="initialize mirror.cfg")
    parser_list.set_defaults(func=_init)

    parser_list = subparsers.add_parser("list", help="list configuration")
    parser_list.set_defaults(func=_list)

    parser_clone = subparsers.add_parser("clone", help="hg clone")
    parser_clone.set_defaults(func=_clone_all)

    parser_setr = subparsers.add_parser(
        "set-remote", help=("set remote (push) path in hgrc")
    )
    parser_setr.set_defaults(func=_setr_all)

    parser_pull = subparsers.add_parser("pull", help="hg pull -u")
    parser_pull.set_defaults(func=_pull_all)

    parser_push = subparsers.add_parser("push", help="hg push")
    parser_push.set_defaults(func=_push_all)

    parser_sync = subparsers.add_parser("sync", help="sync: pull and push ")
    parser_sync.set_defaults(func=_sync_all)

    parser_run = subparsers.add_parser(
        "run", help="run a shell command inside the repo(s)"
    )
    parser_run.set_defaults(func=_run_all)

    for subparser in [
        parser_list,
        parser_clone,
        parser_setr,
        parser_pull,
        parser_push,
        parser_sync,
        parser_run,
    ]:
        _add_arg_repo(subparser)

    for subparser in [parser_push, parser_sync]:
        _add_arg_branch(subparser)

    parser_run.add_argument(
        "cmd", nargs="+", help="shell command to run", default=""
    )

    return parser


def _init(args):
    init_config(args.cfg)


def _list(args):
    try:
        read_config(args.cfg, output=True)
    except OSError:
        cfg_dir = find_cfg_file(args)
        os.chdir(cfg_dir)
        read_config(args.cfg, output=True)


def find_cfg_file(args):
    pwd = os.getcwd()
    if args.cfg is None:
        args.cfg = DEFAULT_CFG_FILE

    for dirname, dirs, files in rwalk(pwd):
        if args.cfg in files:
            break

    return dirname


def _config(args):
    try:
        config = read_config(args.cfg)
    except OSError:
        cfg_dir = find_cfg_file(args)
        os.chdir(cfg_dir)
        config = read_config(args.cfg)

    dirname = os.path.dirname(args.cfg)
    if dirname == "":
        dirname = os.curdir

    os.chdir(dirname)
    if config["defaults"]["ssh"] != "":
        hgopts = ' -e "{}" '.format(os.path.expandvars(config["defaults"]["ssh"]))
    #
    else:
        hgopts = ""

    hggit = config["defaults"].getboolean("use_hg_git")

    return config, hgopts, hggit


def _execute(func, repo, config, *fkeys, **fkwargs):
    def get_fargs(repo):
        """Generate function arguments from fkeys"""
        fargs = []
        for k in fkeys:
            if k is None:
                fargs.append(repo)
            else:
                if config.has_section("repo:" + repo):
                    fargs.append(config["repo:" + repo][k])
                else:
                    raise ValueError("Unconfigured repo: " + repo)

        return fargs

    if repo == "all":
        for repo in get_repos(config.sections()):
            func(*get_fargs(repo), **fkwargs)
    else:
        func(*get_fargs(repo), **fkwargs)


def _all(args, func, key):
    # Go to config file directory and read config
    config, hgopts, hggit = _config(args)

    # Generate function keyword arguments
    fkwargs = dict(hgopts=hgopts, hggit=hggit)
    if hasattr(args, "branch"):
        fkwargs.update({"branch": args.branch})

    # Execute functions on all repo or a selected repo
    _execute(func, args.repo, config, key, None, **fkwargs)


# Assign default parameters for new functions
_clone_all = partial(_all, func=clone, key="pull")
_setr_all = partial(_all, func=set_remote, key="push")
_pull_all = partial(_all, func=pull, key="pull")
_push_all = partial(_all, func=push, key="push")


def _sync_all(args):
    # Go to config file directory and read config
    config, hgopts, hggit = _config(args)

    # Generate function keyword arguments
    fkwargs = dict(hgopts=hgopts, hggit=hggit, branch=args.branch)

    # Execute functions on all repo or a selected repo
    _execute(sync, args.repo, config, None, "pull", "push", **fkwargs)
    config, hgopts, hggit = _config(args)


def run_in_repo(repo, *fargs, **fkwargs):
    os.chdir(repo)
    logger.info(repo)
    print(run(**fkwargs))
    os.chdir("..")


def _run_all(args):
    # Go to config file directory and read config
    config, hgopts, hggit = _config(args)

    # Generate function keyword arguments
    fkwargs = dict(cmd=" ".join(args.cmd), output=False)

    # Execute functions on all repo or a selected repo
    _execute(run_in_repo, args.repo, config, None, None, **fkwargs)


def main(*args):
    parser = get_parser()
    args = parser.parse_args(*args)
    try:
        args.func(args)
    except AttributeError:
        parser.parse_args(["-h"])


if __name__ == "__main__":
    sys.exit(main())
