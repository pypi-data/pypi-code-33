# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import sys

from rpy.cli.utils import SimpleCommand
from rpy.functions.importutils import module_path


class Command(SimpleCommand):

    modules = ['rpy']

    dependencies = (('autopep8', '1.4'), ('isort', '4.3.4'),
                    ('yapf', '0.24.0'), ('autoflake', '1.2'))

    def _module_args(self, *args):

        yield __file__  # autopep main is dropping the first argument

        for module in self.modules:
            yield module_path(module)

        for arg in args:
            yield arg

    def add_arguments(self, parser):
        parser.add_argument('--yapf', dest='use_yapf', default=False, action = 'store_true')

    def handle(self, use_yapf = False, **opts):

        argv = sys.argv

        from autoflake import main

        sys.argv = tuple(
            self._module_args('--in-place', '--remove-duplicate-keys',
                              '--expand-star-import',
                              '--remove-all-unused-imports', '--recursive'))

        main()

        from isort.main import main

        sys.argv = list(
            self._module_args(
                '-rc', '--multi-line', '5', '-a',
                "from __future__ import absolute_import, print_function, unicode_literals"
            ))

        main()

        if use_yapf:

            import yapf

            sys.argv = list(
                self._module_args('--in-place', '--recursive', '--parallel'))

            yapf.run_main()

            sys.argv = argv
