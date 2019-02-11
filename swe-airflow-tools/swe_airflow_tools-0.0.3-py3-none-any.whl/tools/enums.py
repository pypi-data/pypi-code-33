#! -*- coding: utf-8 -*-

from enum import Enum

class EnumDescription(Enum):
    """ Utilizada para associar descrições para os itens execute enum
        para associar uma descrição ao item implementar o atributo
        __descriptions__ da seguinte maneira:

        __descriptions__ = {'attr_name': 'description'}
    """

    @property
    def description(self):
        return self.__descriptions__.get(self.name, '') if hasattr(self, '__descriptions__') else ''


class DatabaseType(EnumDescription):

    postgres = 1

# class StorageType(EnumDescription):
#
#     file = 1
#
# class StorageContentType(EnumDescription):
#
#     json = 1