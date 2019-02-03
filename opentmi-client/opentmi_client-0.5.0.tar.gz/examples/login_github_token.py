from os import getenv
from opentmi_client import OpenTmiClient

client = OpenTmiClient(port=3000)
client.login_with_access_token(access_token=getenv('GITHUB_ACCESS_TOKEN'))
