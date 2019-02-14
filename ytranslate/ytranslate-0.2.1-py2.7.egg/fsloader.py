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

"""Module containing the FSLoader class, described below."""


import os
import os.path
import sys

from ytranslate.catalog import Catalog
from ytranslate.loader import Loader

class FSLoader(Loader):

    """A file system loader of catalogs.

    This class represents a loader for YAML catalogs.  Catalogs
    are contained in files.  Directories are used to create a hierarchy
    of namespaces.  The root directory given in argument is the
    parent directory.  The directories contained in this root
    directory are recursively explored for catalog files.

    """

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.catalogs = {}
        self.namespaces = {}

    def __repr__(self):
        return "<ytranslate.FSLoader (root={})>".format(repr(self.root_dir))

    def load(self):
        """Load the catalogs."""
        root_dir = self.root_dir
        len_root = len(root_dir.split(os.sep))
        for base, dirs, files in os.walk(self.root_dir):
            for file in files:
                if len(file) > 4 and file.endswith(".yml"):
                    fullname = os.path.join(base, file)
                    kwargs = {}

                    # If Python 3, enforce the encoding to 'utf-8'
                    if sys.version_info.major == 3:
                        kwargs["encoding"] = "utf-8"

                    try:
                        with open(fullname, "r", **kwargs) as file:
                            data = file.read()
                    except IOError as e:
                        raise ValueError("cannot load the {} file: " \
                                "{}".format(repr(fullname), e))

                    namespace = ".".join(fullname[:-4].split(
                            os.sep)[len_root + 1:])

                    parent = fullname.split(os.sep)[len_root]
                    if parent.endswith(".yml"):
                        parent = parent[:-4]

                    catalog = Catalog(fullname)
                    catalog.read_YAML(data)
                    if parent != namespace:
                        if parent not in self.catalogs:
                            self.catalogs[parent] = Catalog(parent)
                        parent = self.catalogs[parent]
                        parent.copy_from(catalog,
                                namespace=namespace)
                    else:
                        self.catalogs[namespace] = catalog
                    self.namespaces[namespace] = catalog

    def update_catalog(self, catalog, model, missing="???"):
        """Update the given catalog.

        The catalog specified as a model is used to fill the information
        out, if not provided in the first catalog.  This method can
        be used to create the first catalog or to update it.

        Return the number of updated messages.

        """
        nb = 0
        model = self.catalogs[model]
        if catalog not in self.catalogs:
            catalog = Catalog(catalog)
            self.catalogs[catalog.name] = catalog
        else:
            catalog = self.catalogs[catalog]

        # Write the catalog with missing information
        for key, value in model.messages.items():
            replace = missing
            if isinstance(value, dict):
                replace = value.copy()
                for nkey in replace.keys():
                    replace[nkey] = missing

            if key not in catalog.messages:
                nb += 1
                catalog.messages[key] = replace

        # Finally, write the updated (or newly-created) catalog
        self.save_catalog(catalog)

        return nb

    def save(self):
        """Save all catalogs in the file system."""
        for namespace, catalog in self.namespaces.items():
            self.save_catalog(catalog)

    def save_catalog(self, catalog):
        """Save the specified catalog in the file system.

        Each catalog stores, in its name, the full path leading to
        it.  Assuming the current directory has remained the same
        and the directory structure hasn't significantly changed,
        this method should be able to access the proper
        file and write into it.  An IOError exception is bound to
        be raised if things didn't work for some reason.

        """
        name = catalog.name
        parent_directory = os.path.join(self.root_dir, name)
        kwargs = {}
        # If Python 3, enforce the encoding to 'utf-8'
        if sys.version_info.major == 3:
            kwargs["encoding"] = "utf-8"

        for namespace in self.namespaces.keys():
            if namespace:
                fullname = os.path.join(parent_directory,
                        namespace.replace(".", os.path.sep) + ".yml")
            else:
                parent_directory = self.root_dir
                fullname = os.path.join(parent_directory, name + ".yml")

            # Create the directory structure if necessary
            parent = os.path.split(fullname)[0]
            if not os.path.exists(parent):
                os.makedirs(parent)

            yaml = catalog.write_YAML(namespace)
            with open(fullname, "w", **kwargs) as file:
                file.write(yaml)
