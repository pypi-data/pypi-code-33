import os

import requests

from pyqalx.core.entity import QalxEntity
from pyqalx.core.errors import QalxError


class Item(QalxEntity):
    """QalxEntity with entity_type Item"""
    entity_type = 'item'
    _file_bytes = None

    def read_file(self):
        if "file" not in self.keys():
            raise QalxError("Item doesn't have file data.")
        else:
            response = requests.get(url=self['file']['url'])
            if response.ok:
                self._file_bytes = response.content
                return self._file_bytes
            else:
                raise QalxError("Error with file retrieval: \n\n" + response.text)

    def save_file(self, filepath, filename=None):
        if filename is None:
            filename = self['file']['filename']
        if self._file_bytes is None:
            self.read_file()
        with open(os.path.join(filepath, filename), "wb") as f:
            f.write(self._file_bytes)



