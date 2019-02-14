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

"""Module containing the Loader class, described below."""


class Loader(object):

    """A base class for a catalog loader.

    Loaders should inherit this class, and implement the 'load'
    method.  A loader is used to define a way to load catalogs.
    For instance, FSLoader (File System Loader) loads catalogs from
    the file system.  If you wish to create a new type of loader,
    you can simply inherit this class.  A single loader is used
    by default (see the 'init' funciton in 'ytranslate.tools'),
    although it's possible to create several loaders and work with
    them simultaneously, if the need arises.

    """

    current_loader = None
    current_catalog = None

    def load(self):
        """Load the catalogs."""
        raise NotImplementedError

    def select(self, catalog):
        """Select the catalog of the specified name."""
        type(self).current_catalog = self.catalogs[catalog]
