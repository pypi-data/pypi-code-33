
from igoogle import *

import gsheets



class SheetReader:
    """
    구글에서 명명한 파일명 : '80466616235-7mqvf5ihtkj5pu460lknf3kgc78tf3a5.apps.googleusercontent.com'
    """
    def __init__(self, url):
        self.url = url
        self.client_secret = CLIENT_SECRET_FILE

    def get_sheets(self):
        sheets = gsheets.Sheets.from_files(self.client_secret, '~/storage.json')
        return sheets.get(self.url)
