import requests
import json


class Communication():

  url = ""
  port = 0

  connection = ""

  data = ""

  def __init__(self, url, port):
    self.url = url
    self.port = port
    self.connection = "http://" + self.url + ":" + str(self.port)


  def pull(self):

    response = requests.get(url = self.connection)
    jsonData = json.loads(response.text)
    return jsonData['movement']


  def send(self, data):
    pass
  

  def exit(self):
    pass
