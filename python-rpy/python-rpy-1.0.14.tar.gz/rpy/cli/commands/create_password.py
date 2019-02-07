# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from rpy.cli.utils import SimpleCommand
from rpy.functions.api import fernet
from rpy.functions.encoding import force_text


class Command(SimpleCommand):

    dependencies = (('cryptography', None), )

    def handle(self,
               name=None,
               new_password=None,
               default_password=None,
               default_location=None,
               **opts):

        self.print(force_text(fernet.Fernet.generate_key()))
