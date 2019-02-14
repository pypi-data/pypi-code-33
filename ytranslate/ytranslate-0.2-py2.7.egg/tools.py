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

"""Module containing different tools as functions.

They can be called to interact with the created object of the
'ytranslate' library, including the catalogs and loader.

"""

from ytranslate.fsloader import FSLoader
from ytranslate.loader import Loader

def init(LoaderClass=FSLoader, **kwargs):
    """Load the catalogs at a specified location.

    Depending on the type of loader, the arguments vary.  If the
    default LoaderClass is used, the first argument is the root directory.
    The 'root_dir', the parent directory, is sent to the FSLoader
    class which is to create a hierarchy of catalogs.  The parent
    catalogs bear the name of the namespace (that is their
    directory or their filename without the '.yml' extension).
    For instance:
        init(root_dir="path/to/translations")

    Use the 'select' function to then select a catalog.

    """
    loader = LoaderClass(**kwargs)
    FSLoader.current_loader = loader
    loader.load()

def select(catalog):
    """Select the catalog from the loader.

    The catalog's name must be specified.  If the loader is a
    FSLoader (the default), then the 'root_dir' directory contains
    the parent catalogs.  You should use one of its contained
    directoriess' names, or that of a MYL file without the '.yml'
    extension.  For instance:
        select("en")

    """
    if FSLoader.current_loader:
        FSLoader.current_loader.select(catalog)
    else:
        raise ValueError("the current loader hasn't been selected")

def t(address, count=None, **kwargs):
    """Retrieve the translated message from the selected catalog.

    You can use this function to obtain the translated message,
    corresponding to the address, which must represent the list of
    namespaces separated by '.'.  For instance:
        t("ui.title")

    The hierarchy of messages is defined by the catalog's structure
    (directories and files, if it has been selected by a FSLoader,
    which is the default choice).

    You can also use placeholders as named parameters:
        t("welcome.name", user="John")

    Additionally, you can vary the message according to a number.
    For instance:
        t("notificaiton.emails", 3)

    See the user documentation for a detailed explanation about
    the syntax and corresponding catalogs.

    """
    if FSLoader.current_catalog:
        return FSLoader.current_catalog.retrieve(address, count, **kwargs)

    raise ValueError("no catalog has been selected")
