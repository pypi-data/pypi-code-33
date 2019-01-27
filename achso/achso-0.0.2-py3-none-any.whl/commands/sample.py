#!/usr/bin/env python

from __future__ import print_function
import os
import re

from cement.core.controller import expose

from ..controller import Controller

class Sample(Controller):
    class Meta:
        label = 'sample'
        description = 'Save sample inputs/outpus to files'
        arguments = [
            (['domain'], dict(action='store', nargs=1, help='Domain (e.g. abc001, http://abc001.contest.atcoder.jp/)')),
            (['output_directory'], dict(action='store', nargs='?', help='Path to save files', default='.')),
        ]
        stacked_type = 'nested'

    @expose(hide=True)
    def default(self):
        self._check_config_sample()

        self._login()

        tasks = self._tasks()
        files = []

        self._makedirs(self.app.pargs.output_directory)

        for slug, id_ in tasks:
            self.app.log.debug('processing ' + id_)
            for j, io in enumerate(self._samples(slug)):
                for i, x in enumerate(io):
                    filename = self._filename(i, id_, j + 1)
                    files.append(filename)
                    with open(filename, 'w') as fp:
                        print(x.strip(), file=fp)

        self.app.render({'error': False, 'files': files})

    def _samples(self, url):
        task_res = self.session.get(self._url('tasks/' + url))
        task_res.raise_for_status()

        match = re.finditer('</h3>\s*<pre>(.*?)</pre>', task_res.text, flags=re.DOTALL)
        match = (x.group(1).replace('\r\n', '\n') for x in match)
        samples = [(i, o) for i, o in zip(match, match)]

        # Deduplicate
        samples = [sample for i, sample in enumerate(samples) if samples.index(sample) == i]

        return samples

    def _makedirs(self, path):
        if not os.path.isdir(path):
            return os.makedirs(path)
