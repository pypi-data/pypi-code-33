#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# NM53                                                                         #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program creates and updates backups of GitHub repositories of a user.   #
#                                                                              #
# copyright (C) 2017 Will Breaden Madden, wbm@protonmail.ch                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help                    display help message
    --version                     display version and exit
    --user=TEXT                   GitHub username
    --parallel=BOOL               run git subprocesses in parallel       [default: false]
    --display_commands_only=BOOL  display commands only, do not execute  [default: true]
"""

name        = "NM53"
__version__ = "2019-01-30T1909Z"

import docopt
import json
import os
import subprocess
import sys
import urllib2

def main():
    options               = docopt.docopt(__doc__, version=__version__)
    user                  = options["--user"]
    parallel              = options["--parallel"].lower() == "true"
    display_commands_only = options["--display_commands_only"].lower() == "true"
    URL                   = "https://api.github.com/users/{user}/repos?page=1&per_page=1000".format(user = user)
    if user is None:
        print(__doc__)
        print("no user specified")
        sys.exit()
    response              = urllib2.urlopen(URL)
    HTML                  = response.read()
    JSON                  = json.loads(HTML)
    commands = ""
    for repository in JSON:
        if os.path.isdir(repository["name"]):
            print("repository {name} local copy found -- pull".format(name=repository["name"]))
            command = "cd {directory}; git pull; cd ..".format(directory=repository["name"])
        else:
            print("repository {name} local copy not found -- clone".format(name=repository["name"]))
            command = "git clone {URL}".format(URL = repository["clone_url"])
        if not display_commands_only:
            process = subprocess.Popen(
                [command],
                shell      = True,
                executable = "/bin/bash",
                stdout     = subprocess.PIPE
            )
            if not parallel:
                process.wait()
        else:
            commands = commands + "\n" + command
    if display_commands_only:
        print(commands)
        print("\nNote: This program by default only lists commands, but can execute them. See --help for documentation on this.")

if __name__ == "__main__":
    main()
