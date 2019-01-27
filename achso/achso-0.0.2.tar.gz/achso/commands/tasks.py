#!/usr/bin/env python

from cement.core.controller import expose

from ..controller import Controller

class Tasks(Controller):
    class Meta:
        label = 'tasks'
        description = 'List all tasks'
        arguments = [
            (['domain'], dict(action='store', nargs=1, help='Domain (e.g. abc001, http://abc001.contest.atcoder.jp/)')),
        ]
        stacked_type = 'nested'

    @expose(hide=True)
    def default(self):
        self._login()
        self.app.render({'error': False, 'tasks': self._tasks(dictionary=True)})
