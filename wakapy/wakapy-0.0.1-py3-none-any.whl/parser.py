import json
from typing import List

from wakapy.day import Day


class JsonDict:
    """
    Class that extracts the data from the json file.

    Parameters
    __________

    fp : :class:`str`
        file path, received from :class:`.User`

    Attributes
    ---------
    fp
        :class:`str`
    file
        :class:`dict`
        The whole data.

    """
    def __init__(self, fp: str):
        self.fp = fp
        self.file = self._load_file()
        self._days = [Day(item) for item in self.file['days']]

    def _load_file(self) -> dict:
        with open(self.fp, 'r') as f:
            a = json.load(f)
            return a

    @property
    def user_data(self) -> dict:
        """
        :property:

        :return: :class:`dict` User's data, doesn't containt any :class:`.Day`
        """
        return self.file['user']

    @property
    def days(self) -> List[Day]:
        """
        :property:
        :return: List[:class:`.Day`] The list of days that will be stored in :class:`.User`
        """
        return self._days

    def __repr__(self):
        return f"<'wakapy.{self.__class__.__name__}({self.fp})'>"
