#!/usr/bin/env python
#
# Scriopts to install packages on /cvmfs/lhcbdev.cern.ch/lib
#
#

import logging
from lbdevmanager.GitManager import GitManager
from multiprocessing import Process
import sys
import os
from LbCVMFS import Tools


def install():
    from lbdevmanager.LbInstallManager import LbInstallManager
    installer = LbInstallManager(siteroot=siteroot)
    installer.installFiles(filesToInstall)

if __name__ == "__main__":
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=FORMAT)
    logging.getLogger().setLevel(logging.DEBUG)

    siteroot = "/cvmfs/lhcbdev.cern.ch/lib"
    repo = os.path.expandvars("${HOME}/conf/cvmfsdev-sw")

    gitManager = GitManager(repo_path=repo)
    filesToInstall = gitManager.GetFilesDiffToInstall()

    if len(filesToInstall) == 0:
        gitManager.UpdateTags()
        logging.info("We are up to date, exiting")
        sys.exit(0)

    # Starting a transaction on CVMFS
    with Tools.cvmfsTransaction():
        try:
            # We start the method in a subprocess to make sure all fds are
            # closed on CVMFS
            # after we are done, or we cannot publish
            p = Process(target=install)
            p.start()
            p.join()

            import subprocess
            subprocess.call("checkfds")
        except Exception, e:
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)

    # Update tags
    gitManager.UpdateTags()
