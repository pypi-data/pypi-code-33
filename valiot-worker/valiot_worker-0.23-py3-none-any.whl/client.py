import requests
import queries
import json
import os

# from dotenv import load_dotenv
# load_dotenv()

class GraphQLClient:
  def __init__(self, endpoint):
    self.endpoint = endpoint
    self.token = None
    self.headername = None

  def execute(self, query, variables=None):
    return self._send(query, variables)

  def inject_token(self, token, headername='Authorization'):
    self.token = token
    self.headername = headername

  def _send(self, query, variables):
    data = {'query': query,
    'variables': variables}
    headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
      }
    if self.token is not None:
      headers[self.headername] = '{}'.format(self.token)
    response = requests.post(self.endpoint, json=data, headers=headers)
    if response.status_code == 200:
      return response.json()
    else:
      raise Exception(
        "Query failed to run by returning code of {}. {}".format(
          response.status_code, query))

class Worker(GraphQLClient):
  def __init__(self, *args, **kwargs):
    GraphQLClient.__init__(self, *args, **kwargs)
  
  def request_waiting_jobs(self):
    data = self.execute(queries.all_jobs)
    errors = data.get('errors', None)
    if errors:
      return False, errors[0]['message']
    else:
      return True, data['data']['jobs']

  def update_job(self, variables):
    return self.execute(queries.update_job, variables)['data']['updateJob']['successful']

# Web Service configuration
endpoint = os.environ.get('API')
token = os.environ.get('TOKEN')
worker=Worker(endpoint)
worker.inject_token(token)