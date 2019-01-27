#!/usr/bin/env python

from cement.core.controller import expose

from ..controller import Controller

class Languages(Controller):
    class Meta:
        label = 'languages'
        description = 'List all languages available'
        arguments = [
            (['domain'], dict(action='store', nargs=1, help='Domain (e.g. abc001, http://abc001.contest.atcoder.jp/)')),
        ]
        stacked_type = 'nested'

    @expose(hide=True)
    def default(self):
        self._login()
        self.app.render({'error': False, 'languages': self._languages()})
