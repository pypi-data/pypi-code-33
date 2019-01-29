from vexbi import Base, Response, Client
import mimetypes
from os.path import basename
import requests

class API(Base):
  def __init__(self, app_id, secret_key):
    client = Client(app_id, secret_key)
    Base.__init__(self, client)

  def use_sandbox(self):
    self.client.use_sandbox()

  def create_order(self, order_data):
    return self.post(data=order_data, url=self.url('orders'))

  def delete_order(self, order_id):
    return self.post(data={ 'id': order_id }, url=self.url('order/delete'))

  def clear_all(self, data=None):
    return self.post(data=data, url=self.url('orders/clear'))

  def get_orders(self, market, query={}):
    url = self.url('orders?market={}'.format(market))
    return self.get(url=url, data=query)

  def get_order(self, order_id):
    return self.get(url=self.url('order?id={}'.format(order_id)))

  def get_account_info(self):
    return self.get(url=self.url('members/me'))

  def get_available_markets(self):
    return self.get(url=self.url('markets'))

  def tickers(self):
    return self.get(url=self.url('tickers'))

  def trades(self, market, query={}):
    url = self.url('trades?market={}'.format(market))
    return self.get(url=url, data=query)

  def my_trades(self, market, query={}):
    url = self.url('trades/my?market={}'.format(market))
    return self.get(url=url, data=query)
