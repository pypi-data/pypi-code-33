from .api_auth import RequestsApiAuth
from .config import PRODUCTION_URL, SANDBOX_URL

class Client:
  def __init__(self, app_id, secret_key):
    self.sandbox = False
    self.auth = RequestsApiAuth(app_id, secret_key)
    self.base_url = PRODUCTION_URL

  def use_sandbox(self):
    self.sandbox = True
    self.base_url = SANDBOX_URL

  def set_base_url(self, base_url):
    self.base_url = base_url

  def url(self):
    return self.base_url + '/api/v2/{path}'
