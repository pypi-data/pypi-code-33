#!/usr/bin/env python

import difflib

from cement.core.controller import expose

from ..controller import Controller
from ..exception import IllegalCommandException, UnexpectedResponseException

class Submit(Controller):
    class Meta:
        label = 'submit'
        description = 'Submit a file'
        arguments = [
            (['domain'], dict(action='store', nargs=1, help='Domain (e.g. abc001, http://abc001.contest.atcoder.jp/)')),
            (['task_id'], dict(action='store', nargs=1, help='Short task ID (e.g. A)')),
            (['filename'], dict(action='store', nargs=1, help='Path to file to submit')),
            (['language'], dict(action='store', nargs=1, help='Language (by name, e.g. "C++14 (GCC 5.3.0)")')),
        ]
        stacked_type = 'nested'

    @expose(hide=True)
    def default(self):
        self._login()

        with open(self.app.pargs.filename[0]) as fp:
            source_code = fp.read()

        language_dict = self._languages(dictionary=True)
        language_name = self.app.pargs.language[0]
        if language_name not in language_dict:
            closest = difflib.get_close_matches(language_name, language_dict.keys(), len(language_dict))
            if len(closest) > 0:
                raise IllegalCommandException('Language name invalid, did you mean: {}'.format(', '.join(closest)))
            else:
                raise IllegalCommandException('Language name invalid')

        language_id = language_dict[language_name]

        tasks = self._tasks(dictionary=True)

        for task in tasks:
            if task['id'] == self.app.pargs.task_id[0]:
                internal_id = task['internal_id']
                break
        else:
            raise IllegalCommandException('Task not found (choose from: {})'.format(', '.join([task['id'] for task in tasks])))

        submit_res = self.session.post(self._url('submit'),
                          {'__session': self.session_token,
                           'task_id': internal_id,
                           'language_id_{}'.format(internal_id): language_id,
                           'source_code': source_code})

        if 'submissions/me#' not in submit_res.url:
            raise UnexpectedResponseException('Submission failed')
        else:
            self.app.render({'error': False, 'submission_id': submit_res.url.split('submissions/me#')[-1]})
