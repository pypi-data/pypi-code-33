#!/usr/bin/env python

from __future__ import absolute_import
import collections
import subprocess

from cement.core.controller import CementBaseController, expose
import lxml.html
import requests

from .exception import IllegalConfigurationException, LoginException, UnexpectedResponseException

class Controller(CementBaseController):
    class Meta:
        label = 'base'
        description = 'AtCoder Helper Suite'

    user_agent = 'AchSo/0.0.1'

    domain = None
    session = None

    def _login(self):
        if self.session is None:
            self.session = requests.Session()
            self.session.headers.update({'User-Agent': self.user_agent})

        # check if the contest is open
        top_res = self.session.get(self._url(''))
        top_res.raise_for_status()
        if '<title>404' in top_res.text: # AtCoder responds with 200, even if the site is not open
            raise LoginException('Contest page not found')

        login_res = self.session.post(self._url('login'),
                                      {'name': self.app.config.get('credentials', 'id'),
                                       'password': self.app.config.get('credentials', 'password')})
        login_res.raise_for_status()
        if login_res.url.endswith('login'):
            raise LoginException('Credentials invalid')

    def _languages(self, dictionary=False):
        submit_res = self.session.get(self._url('submit'))
        submit_res.raise_for_status()

        html = lxml.html.fromstring(submit_res.text)
        options = html.cssselect('select.submit-language-selector option')
        languages = collections.OrderedDict((o.text_content(), o.get('value')) for o in options)

        self.session_token = html.cssselect('input[name=__session]')[0].get('value')

        if dictionary:
            return languages
        else:
            return list(languages.keys()) # explicit conversion for Python 3

    def _tasks(self, dictionary=False):
        assignment_res = self.session.get(self._url('assignments'))
        assignment_res.raise_for_status()

        html = lxml.html.fromstring(assignment_res.text)
        tasks = []
        for tr in html.cssselect('tbody tr'):
            tds = tr.cssselect('th, td')
            links = tr.cssselect('a')
            slug = links[0].get('href')
            if not slug.startswith('/tasks/'):
                raise UnexpectedResponseException('assignments (slug)')
            internal_id = links[2].get('href')
            if not internal_id.startswith('/submit?task_id='):
                raise UnexpectedResponseException('assignments (internal_id)')

            tasks.append({
                'slug': slug[len('/tasks/'):],
                'id': links[0].text_content().strip(),
                'title': links[1].text_content().strip(),
                'time_limit': tds[2].text_content().strip(),
                'memory_limit': tds[3].text_content().strip(),
                'internal_id': internal_id[len('/submit?task_id='):],
            })

        if dictionary:
            return tasks
        else:
            return [(t['slug'], t['id']) for t in tasks]

        # tasks = re.findall('<a class="linkwrapper" href="/tasks/(.*)">(.*)</a>', assignment_res.text)
        # tasks = iter(tasks)

        # if dictionary:
        #     return [{'slug': slug, 'id': id_, 'title': title} for (slug, id_), (_, title) in zip(tasks, tasks)]
        # else:
        #     return [(slug, id_, title) for (slug, id_), (_, title) in zip(tasks, tasks)]

    def _url(self, path):
        if self.domain is None:
            domain = self.app.pargs.domain[0]

            if '.' not in domain:
                domain = 'https://{}.contest.atcoder.jp'.format(domain)

            if not domain.startswith('http'):
                domain = 'https://' + domain

            self.domain = domain

        return self.domain + '/' + path

    def _filename(self, out, id_, number):
        return (self.app.pargs.output_directory + '/' +
                self.app.config.get('sample', 'filename')
                .replace('%inout%', 'out' if out else 'in')
                .replace('%id%', str(id_))
                .replace('%number%', str(number)))

    def _check_config_sample(self):
        filename = self.app.config.get('sample', 'filename')

        if '%inout%' not in filename:
            raise IllegalConfigurationException('%inout% must be included in config.sample.filename')

        if '%id%' not in filename:
            raise IllegalConfigurationException('%id% must be included in config.sample.filename')

        if '%number%' not in filename:
            raise IllegalConfigurationException('%number% must be included in config.sample.filename')

    def _run_shell_command(self, command, stdin):
        proc = subprocess.Popen([command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open(stdin, 'rb') as fp:
            stdout, stderr = proc.communicate(fp.read())

        if type(stdout) == type('str'): # Python 2
            return stdout, stderr
        else: # Python 3
            return stdout.decode('utf-8'), stderr.decode('utf-8')
