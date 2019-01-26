from argparse import ArgumentParser
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import bordered
import os
from plumbum.cmd import git
from plumbum import local


def _args():
    parser = ArgumentParser()
    parser.add_argument('--checkout')
    parser.add_argument('--prune', action='store_true')
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()
    src_dir = Dodo.get_config('/ROOT/src_dir')
    for repo in (os.listdir(src_dir) + ['.']):
        repo_dir = os.path.join(src_dir, repo)
        if os.path.exists(os.path.join(repo_dir, '.git')):
            with local.cwd(repo_dir):
                if args.prune:
                    print(git('remote', 'prune', 'origin'))

                print(bordered(repo))
                if args.checkout:
                    try:
                        git('checkout', args.checkout)
                    except:
                        print('Could not checkout to %s' % args.checkout)
                        pass
                print(git('rev-parse', '--abbrev-ref', 'HEAD'))
