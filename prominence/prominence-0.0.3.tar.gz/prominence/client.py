from collections import namedtuple
import requests

class ProminenceClient(object):
    """
    PROMINENCE client class
    """

    # Named tuple containing a return code & data object
    Response = namedtuple("Response", ["return_code", "data"])

    def __init__(self, url=None, token=None):
        self._url = url
        self._timeout = 10
        self._headers = {"Authorization":"Bearer %s" % token}

    def list(self, completed, all, num, constraint):
        """
        List running/idle jobs or completed jobs
        """

        params = {}

        if completed:
            params['completed'] = 'true'

        if num:
            params['num'] = num

        if all:
            params['all'] = 'true'

        if constraint:
            params['constraint'] = constraint

        try:
            response = requests.get(self._url + '/jobs', params=params, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data=response.json())
        elif response.status_code < 500:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

    def create(self, job):
        """
        Create a job
        """
        return self.create_from_json(job.to_json())

    def create_from_json(self, job):
        """
        Create a job from JSON description
        """
        data = job
        try:
            response = requests.post(self._url + '/jobs', json=data, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})
        if response.status_code == 201:
            if 'id' in response.json():
                return self.Response(return_code=0, data={'id': response.json()['id']})
        elif response.status_code < 500:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})        
        return self.Response(return_code=1, data={'error': 'unknown'})

    def delete(self, job_id):
        """
        Delete the specified job
        """
        try:
            response = requests.delete(self._url + '/jobs/%d' % job_id, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data={})
        else:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

    def describe(self, job_id, completed=False):
        """
        Describe a specific job
        """
        if completed:
            completed = 'true'
        else:
            completed = 'false'
        params = {'completed':completed, 'num':1}

        try:
            response = requests.get(self._url + '/jobs/%d' % job_id, params=params, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data=response.json())
        elif response.status_code < 500:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

    def stdout(self, job_id):
        """
        Get standard output from a job
        """

        try:
            response = requests.get(self._url + '/jobs/%d/0/stdout' % job_id, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data=response.content)
        else:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

    def stderr(self, job_id):
        """
        Get standard error from a job
        """

        try:
            response = requests.get(self._url + '/jobs/%d/0/stderr' % job_id, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data=response.content)
        else:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})
