from vexbi import Response
import requests

class Base(object):
  def __init__(self, client):
    object.__setattr__(self, 'sandbox', False)
    object.__setattr__(self, 'client', client)
    object.__setattr__(self, 'response', Response())
    self.id = None

  def url(self, path=None):
    return self.client.url().format(path=path)

  def post(self, url, data=None, json=None):
    response = requests.post(
      url=url,
      auth=self.client.auth,
      data=data,
      json=json
    )
    self.set_data(response)
    return self.get_data()

  def put(self, url, data=None, json=None):
    response = requests.put(url, auth=self.client.auth, json=data)
    self.set_data(response)
    return self.get_data()

  def get(self, url, data=None, json=None):
    response = requests.get(url, auth=self.client.auth, params=data, json=json)
    self.set_data(response)
    return self.get_data()

  def delete(self, url, data=None):
    response = requests.delete(url, auth=self.client.auth, json=data)
    self.set_data(response)
    return self.get_data()

  def set_data(self, response):
    self.response.set_response(response)

  def get_data(self):
    return self.response.get_response()

  def __setattr__(self, name, value):
    self.response.set(name, value)

  def __getattr__(self, name):
    return self.response.get(name)
