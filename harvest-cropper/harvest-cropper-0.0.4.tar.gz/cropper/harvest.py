import requests


class Harvest(object):
    """
    A class to interact with Harvest returning JSON objects from its API
    """

    API_URL = "https://api.harvestapp.com/api/v2/"

    def __init__(self, logger, token, accountid):
        """
        The constructor gets a logger and the credentials to
        store at the instance a requests Session with the 
        proper headers to authenticate against Harvest API.

        Parameters:
            logger (logging): a logger to use
            token (str): the auth token
            accountid (int): the account identifier
        """
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            'Harvest-Account-ID': accountid,
            'Authorization': 'Bearer {}'.format(token)
        })

    def _call(self, endpoint, parameters={}):
        """
        Private method to call a Harvest API endpoint

        Parameters:
            endpoint (str): the API endpoint url section
            parameters (dict): the parameters to add to the GET request
        """
        self.logger.debug(
            'Making a request to the endpoint {} with parameters: {}'.format(endpoint, str(parameters)))
        r = self.session.get(url=self.API_URL + endpoint, params=parameters)
        if r.status_code == 200:
            return r.json()
        else:
            self.logger.debug(r.text)
            raise Exception('Error accessing the {} endpoint'.format(endpoint))

    def _get_paged_results(self, endpoint, objectid, parameters={}):
        """
        Private method to get all the results of a paged endpoint

        Parameters:
            endpoint (str): the API endpoint url section
            objectid (str): the key of the array to extract from 
                            the returning JSON
            parameters (dict): the parameters to add to the GET request 
        """

        first_request = self._call(
            endpoint, {**parameters, **{'per_page': 100, 'page': 1}})
        results = first_request[objectid]
        total_pages = first_request['total_pages']
        entries = first_request['total_entries']
        if total_pages > 1:
            self.logger.debug('The request needs up to {} paged requests for a total of {} entries'.format(
                total_pages, entries))
            for page in range(2, total_pages+1):
                request = self._call(
                    endpoint, {**parameters, **{'per_page': 100, 'page': page}})
                results = results + request[objectid]
        return results

    def check(self):
        """
        Just returns information about the requesting user
        """
        return self._call('/users/me.json')

    def projects(self, active, client=None):
        """
        Gets a list of projects

        Parameters:
            active (str): gets the list of active, inactive or all
                          projects
            client (int): return the projects linked to an specific
                          client
        """
        params = {}
        if active == 'active':
            params['is_active'] = "true"
        elif active == 'inactive':
            params['is_active'] = "false"

        if client:
            params['client_id'] = client

        return self._get_paged_results('/projects', 'projects', params)

    def project(self, project_id):
        """
        Gets details of an specific project

        Parameters:
            project_id (int): the project identifier
        """
        return self._call('/projects/{}'.format(project_id))

    def company(self):
        """
        Gets company details associated to the Harvest account
        """
        return self._call('/company')

    def clients(self, active="all"):
        """
        Gets a list of clients

        Parameters:
            active (str): filter the active clients (all, inactive, active)
        """
        params = {}
        if active == 'active':
            params['is_active'] = "true"
        elif active == 'inactive':
            params['is_active'] = "false"

        return self._get_paged_results('/clients', 'clients', params)

    def users(self, active="all"):
        """
        Gets a list of users

        Parameters:
            active (str): filter the active users (all, inactive, active)
        """
        params = {}
        if active == 'active':
            params['is_active'] = "true"
        elif active == 'inactive':
            params['is_active'] = "false"

        return self._get_paged_results('/users', 'users', params)

    def task_assignments(self, projectid=None):
        """
        Gets the list of tasks associated to a project

        Parameters:
            projectid (int): the project identifier
        """
        if projectid:
            endpoint = 'projects/{}/task_assignments'.format(projectid)
        else:
            endpoint = '/task_assignments'
        return self._get_paged_results(endpoint, 'task_assignments')

    def time_entries(self, **kwargs):
        """
        Gets the list of timesheet entries associated to a project

        Parameters:
            projectid (int): the project identifier
        """
        params = {}
        for key, value in kwargs.items():
            if value:
                if key == "_from":
                    params['from'] = value
                else:
                    params[key] = value

        return self._get_paged_results('/time_entries', 'time_entries', params)

    def time_entry(self, time_entry_id):
        """
        Retrieves a single time entry

        Parameters:
            time_entry_id(int) Entry identifier
        """
        return self._call('/time_entries/{}'.format(time_entry_id))

    def update_time_entry(self, time_entry_id, project_id, task_id, notes=None):
        """
        Updates a timesheet entry to be associated to a project and task

        Parameters
            time_entry_id (int): the time entry identifier
            project_id (int): the project identifier
            task_id (int): the task identifier
        """
        url = self.API_URL + '/time_entries/{}'.format(time_entry_id)
        params = {
            'project_id': project_id,
            'task_id': task_id
        }

        if notes:
            params['notes'] = notes

        self.logger.debug('Calling PATCH for updating the time entry')
        r = self.session.patch(url=url, params=params)

        if r.status_code == 200:
            return r.json()
        else:
            self.logger.debug(r.text)
            raise Exception('Error accessing the /time_entries endpoint')
