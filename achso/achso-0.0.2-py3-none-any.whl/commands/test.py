#!/usr/bin/env python

from __future__ import print_function
try:
    from future_builtins import zip
except ImportError: # wtf
    pass
import glob

from cement.core.controller import expose
import cement.core.exc

from ..controller import Controller

class Test(Controller):
    class Meta:
        label = 'test'
        description = 'Run automated tests'
        arguments = [
            (['id'], dict(action='store', nargs=1, help='Task ID')),
            (['command'], dict(action='store', nargs=1, help='Command to execute')),
            (['output_directory'], dict(action='store', nargs='?', help='Path to saved files', default='.')),
        ]
        stacked_type = 'nested'

    @expose(hide=True)
    def default(self):
        self._check_config_sample()

        count = 0
        correct = 0
        wrong = 0
        output = []
        try:
            for i, o in zip(*[glob.iglob(self._filename(i, self.app.pargs.id[0], '*')) for i in [False, True]]):
                # TODO: Parallel execution
                count += 1
                self.app.log.debug('case #{}: {}, {}'.format(count, i, o))

                with open(o) as fp:
                    expected = fp.read()

                system, stderr = self._run_shell_command(self.app.pargs.command[0], i)

                correct += expected == system
                wrong += expected != system
                output.append({'expected': expected, 'system': system, 'stderr': stderr})
        except cement.core.exc.CaughtSignal as e:
            self.app.exit_code = e.signum

        self.app.render({'error': False, 'correct': correct, 'wrong': wrong, 'output': output})
