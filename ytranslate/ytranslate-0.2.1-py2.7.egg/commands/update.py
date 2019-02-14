# Copyright (c) 2015, LE GOFF Vincent
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of ytranslate nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""Module containing the UpdateCommand class, described below."""

from __future__ import print_function
import os
import os.path
import sys

from ytranslate.commands.base import BaseCommand
from ytranslate.fsloader import FSLoader

class UpdateCommand(BaseCommand):

    """Commands 'update'.

    This command updates a given catalog with a default model.

    """

    name = "update"

    def __init__(self, parser=None):
        BaseCommand.__init__(self, parser)
        parser.add_argument("directory",
                help="the path to the directory containing the catalogs")
        parser.add_argument("catalog", nargs='?',
                help="the catalog name to be created or updated")
        parser.add_argument("-m", "--model", nargs='?',
                default="en", help="the model catalog to be used")

    def execute(self, args):
        """Execute the command."""
        root_dir = args.directory
        if not os.path.exists(root_dir):
            print("The {} directory doesn't exist".format(repr(root_dir)),
                    file=sys.stderr)
            sys.exit(1)
        elif not os.path.isdir(root_dir):
            print("The {} path doesn't lead to a directory".format(
                    repr(root_dir)), file=sys.stderr)
            sys.exit(1)

        loader = FSLoader(root_dir)
        loader.load()
        nb = loader.update_catalog(args.catalog, args.model)
        print("Successfully updated the '{}' catalog ({})".format(
                args.catalog, nb))
