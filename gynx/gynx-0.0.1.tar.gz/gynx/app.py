#!/usr/bin/python2.7

from core import Gynx
from files.readers import *
from files.differences import *
from files.operations import *
#import argparse

class GynxApp(object):

    #@property
    #def arguments(self):
    #    parser = argparse.ArgumentParser()
    #    parser.add_argument("verbose", help="Run in verbose mode", action="store_true")
    #    parser.add_argument("dry", help="Run dry i.e. do not perform sync operations", action="store_true")
    #    return parser.parse_args()

    @property
    def verbose(self):
        return 'verbose' in sys.argv

    @property
    def dry_run(self):
        return 'dry' in sys.argv

    def run(self):
        gynx = Gynx()
        if self.verbose:
            print(gynx)
            gynx.print_info()
        local_reader = LocalFileReader(src=gynx.appdir, rootdir=gynx.root, quiet=gynx.quiet)
        local = local_reader.files
        remote_reader = RemoteFileReader(src=gynx.appdir, service=gynx.service, info=gynx.get_info(), quiet=gynx.quiet)
        remote = remote_reader.files
        differences = Differences(
            remote_files=remote,
            local_files=local,
            previous=remote_reader.load(),
            root=gynx.root,
            initial=remote_reader.initial
        )
        if self.dry_run:
            differences.print_all()
        else:
            operations = SyncOperations(
                service=gynx.service,
                changes=differences.all(),
                remote=remote,
                local=local,
                root=gynx.root,
                rf=remote_reader.remote_folders
            )
            operations.run()

app = GynxApp()
app.run()
