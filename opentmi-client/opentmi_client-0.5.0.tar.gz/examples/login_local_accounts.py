from os import getenv
from opentmi_client import OpenTmiClient

client = OpenTmiClient(port=3000)
client.login(username=getenv('USERNAME'), password=getenv('PASSWORD'))
