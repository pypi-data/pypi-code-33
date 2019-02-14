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

"""Module containing the Catalog class, described below."""

import yaml

try:
    unicode
except NameError:
    unicode = str

class Catalog:

    """A losely-defined catalog for translation.

    A Catalog object contains a hierarchy of matches and sub-catalogs.
    This hierarchy, established by the developer in charge of
    the translations, must be reproduced for every language that
    the software should support.  These catalogs are defined as
    YML files on the file system, although they may be created and
    expanded programmatically.  Also note that catalogs can easily
    be used in other situations, when simple and complex matching applies.

    A simple catalog defined in YAML, en.yml, may look like this:
        ui:
            title: Ytranslator
            login:
                unknown: Welcome.  Perhaps you would wish to login?
                user: Welcome, {user}!  Glad to see you back.

    In this example, the catalog 'en' contains a single namespace:
    'ui'.  In it are a simple message, 'title', and anther namespace,
    'login', which contains two messages.  You could use this catalog
    in your code like this:
        from ytranslate import select, t
        # Select the 'en' catalog that we just defined
        select("en")
        # Retrive the title of the GUI application
        title = t("ui.title")
        # Is the user logged in?
        if user.logged_in:
            print t("ui.login.user", name="Jean")
        else:
            print t("ui.login.unknown")

    Of course, having a single catalog doesn't make much sense.  But
    if you have a catalog in a different language using exactly the
    same hierarchy, things look very interesting.  You could have
    a 'fr.yml' catalog for instance:
        ui:
            title: Ytraducteur
            login:
                unknown: Bienvenue. Souhaiteriez-vous vous connecter ?
                user: Bienvenue, {user} !  Heureux de vous revoir.

    You can try to run the same code selecting 'fr' for a catalog
    this time.  The concept is pretty simple, but the possibilities
    are endless.  Most catalogs of complex applications are defined
    in folders and sub-folers, which are just new namespaces in
    the hierarchy.

    """

    def __init__(self, name):
        self.name = name
        self.messages = {}

    def __repr__(self):
        return "<ytranslate.Catalog {}>".format(repr(self.name))

    def read_dictionary(self, dictionary, parent=""):
        """Read a namespace defined in a dictionary."""
        for name, entry in dictionary.items():
            name = str(name)
            if parent:
                name = parent + "." + name

            if isinstance(entry, dict):
                if all(str(key).rstrip("+").isdigit() for key in entry):
                    copied = {}
                    for key, value in entry.items():
                        copied[str(key)] = unicode(value)

                    self.messages[name] = copied
                else:
                    self.read_dictionary(entry, parent=name)
            else:
                self.messages[name] = unicode(entry)

    def read_YAML(self, content):
        """Fill the catalog using this YAML content.

        Te content must be a str containing YAML code that should
        represent a dictionary.  The whole dictionary will be integrated
        in the 'messages' dictionary.  Namespaces can be deefined
        in the YAML document, but they will be "flattened out".
        For instance, if the content contains the following string:
            file: Fichier
            edit: Édition
            view: Affichage
            connection:
                connected: Connecté
                connecting: Connexion en cours
                error: Connexion impossible

        Then the following messages will be created or updated:
        {
            'file': 'Fichier',
            'edit': 'Édition',
            'view': 'Affichage',
            'connection.connected': 'Connecté',
            'connection.connecting': 'Connexion en cours',
            'connection.error': 'Connexion impossible',
        }

        """
        try:
            data = yaml.safe_load(content)
        except yaml.parser.ParserError as err:
            # Use a newly-defined expression
            raise ValueError("an error occurred while parsing the " \
                    "YAML content:\n{}".format(str(err)))

        if isinstance(data, dict):
            self.read_dictionary(data)
        else:
            raise ValueError("the YAML content doesn't describe a dictionary")

    def copy_from(self, catalog, namespace=""):
        """Copy the messages of the catalog provided as a parameter.

        The 'namespace' parameter can create sub-namespaces for
        a whole catalog.

        """
        for name, message in catalog.messages.items():
            if namespace:
                name = namespace + "." + name

            self.messages[name] = message

    def write_dictionary(self):
        """Write the nested dictionary.

        Namespaces are used to create a nested dictionary.  The
        'ui.title' message would be converted in a dictionary with
        a key 'ui', and as a value another dictionary containing
        in key 'title' and in value the message's value.  The
        process is exactly the opposite of the 'read_dictionary'
        method.

        """
        keys = sorted(self.messages.keys())
        nested = {}
        for key in keys:
            value = self.messages[key]

            # Split the key in namespaces separated by '.'
            last_namespace = key.split(".")[-1]
            namespaces = key.split(".")[:-1]
            current = nested
            for namespace in namespaces:
                if namespace not in current:
                    current[namespace] = {}

                current = current[namespace]

            current[last_namespace] = value

        return nested

    def write_YAML(self):
        """Return the nested content as YAML."""
        nested = self.write_dictionary()
        return yaml.safe_dump(nested, indent=4, width=79,
                default_flow_style=False)

    def retrieve(self, address, count=None, **kwargs):
        """Retrieve the message using the specified address.

        The address is a string of namespaces separated by '.'.
        For instance, "ui.greeting.user".  This address must match
        both the directory/file structure and the internal catalog
        structure.

        It is possible to specify placeholders in the message.  For
        instance, let's say you have a message defined like this
        in your YAML catalog:
            greeting: Hello, {name}!

        In the call to 'retrieve', you will be able to specify
        the name:
            message = catalog.retrieve("greeting", name="John")
            # message will contain "Hello, John!"

        You can also alter the message depending on a number
        (singular and plural in English, or a more specific variation
        in Russian, for instance).  The full syntax is described
        in the 'retrieve_count' method.

        """
        message = self.messages.get(address)
        if count is None and message is None:
            raise ValueError("address {} cannot be found in this " \
                    "catalog".format(repr(address)))

        if count is not None:
            message = self.retrieve_count(address, count, **kwargs)

        return message.format(count=count, **kwargs)

    def retrieve_count(self, address, count, **kwargs):
        """Retrieve a message when a 'count' indicator is present.

        The 'retrieve' method calls 'retrieve_count' if necessary.
        This method shouldn't be called directly.

        A 'count' indicator can be used to alter the message regarding singular, plural or other rules that may apply to the language depending on a number of items.  Definition a group of message in a catalog is simple:  A new dictionary has to be specified instead of just a message.  For instance:
            emails:
                0: You have no email.
                1: You have one email.
                2+: You have {count} emails.

        Then you can simply ask the 'retrieve' method to find the proper message according to the 'count' indicator:
            t("emails", 2)
            # Which will retrieve the message 'You have 2 emails.'

        This second dictionary defined in YAML must contain only
        numbers as keys, or a number followed by the '+' sign,
        which means "either that number of more".  For instance,
        '5+' means either 5 or more.  This way, you can configure
        the catalog to different singular and plural rules
        depending on the language.

        """
        equal = lambda a, b: a == b
        greater = lambda a, b: a >= b
        messages = self.messages.get(address, {})
        if messages is None:
            raise ValueError("address {} cannot be found in this " \
                    "catalog".format(repr(address)))
        elif not isinstance(messages, dict):
            raise ValueError("the message at {} has to be " \
                    "retrieved with a 'count' indicator, though " \
                    "at this address aren't several values".format(
                    repr(address)))

        message = None
        for key in sorted(messages.keys(), reverse=True):
            value = messages[key]
            compare = equal
            if key.endswith("+"):
                key = key[:-1]
                compare = greater

            if not key.isdigit():
                raise ValueError("message {}: {} isn't a valid " \
                        "number.".format(repr(address), key))

            key = int(key)
            if compare(count, key):
                message = value
                break

        if message is None:
            raise ValueError("address {}: no proper message " \
                    "to be displayed with a count of {}".format(
                    repr(address), count))

        return message
