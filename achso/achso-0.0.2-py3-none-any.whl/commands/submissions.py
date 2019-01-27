#!/usr/bin/env python

import re

from cement.core.controller import expose
import lxml.html

from ..controller import Controller
from ..exception import UnexpectedResponseException

class Submissions(Controller):
    class Meta:
        label = 'submissions'
        description = 'List all submissions'
        arguments = [
            (['domain'], dict(action='store', nargs=1, help='Domain (e.g. practice, http://practice.contest.atcoder.jp/)')),
            (['-p', '--preserve-judging-status'], dict(action='store_true', help='Preserve the original status string (like "2/7") while judging')),
            (['-1', '--only-first'], dict(action='store_true', help='Show only the first AC (or the latest, if there is no such one) submission submission for each task')),
        ]
        stacked_type = 'nested'

    @expose(hide=True)
    def default(self):
        self._login()
        self.app.render({'error': False, 'submissions': self._submissions()})

    def _submissions(self):
        raw_html = self.session.get(self._url('submissions/me')).text
        html = lxml.html.fromstring(raw_html)
        submissions = [self._process_tr(tr) for tr in html.cssselect('tbody tr')]

        if self.app.pargs.only_first:
            passed = set()
            first = {}

            for submission in reversed(submissions):
                if submission['slug'] not in passed:
                    first[submission['slug']] = submission
                    if submission['status'] == 'AC':
                        passed.add(submission['slug'])

            return list(first.values()) # explicit conversion for Python 3
        else:
            return submissions

    def _process_tr(self, tr):
        tds = tr.cssselect('th, td')
        qlink = tds[1].cssselect('a')[0].get('href')
        if not qlink.startswith('/tasks/'):
            raise UnexpectedResponseException('submissions/me (qlink)')
        slink = tds[-1].cssselect('a')[0].get('href')
        if not slink.startswith('/submissions/'):
            raise UnexpectedResponseException('submissions/me (slink)')
        status = tds[4].text_content()

        dic = {
            'submission_id': slink[len('/submissions/'):],
            'created_time': tds[0].text_content(),
            'slug': qlink[len('/tasks/'):],
            'title': tds[1].text_content(),
            'language_name': tds[2].text_content(),
            'score': self._int_or_float(tds[3].text_content()),
            'status': status,
        }

        judging = re.search('^(?P<current>\d+)/(?P<total>\d+)', status)
        if judging:
            if not self.app.pargs.preserve_judging_status:
                dic['status'] = 'JUDGING'
            dic['judge_progress'] = {k: int(v) for k, v in judging.groupdict().items()}

        if len(tds) == 8: # AC
            dic['exec_time'] = tds[5].text_content()
            dic['memory_usage'] = tds[6].text_content()
        elif len(tds) != 6: # Overreaction...?
            raise UnexpectedResponseException('submissions/me (table)')

        return dic

    def _int_or_float(self, s):
        if s == '-':
            return None
        try:
            return int(s)
        except ValueError:
            return float(s)
