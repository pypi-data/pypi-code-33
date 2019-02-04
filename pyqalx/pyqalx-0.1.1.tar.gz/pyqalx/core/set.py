from pyqalx.core.entity import QalxEntity


class Set(QalxEntity):
    """QalxEntity with entity_type Set

    """
    entity_type = 'set'


    def add_item(self, item):
        """add an item to a set

        :param item:
        :type item: pyqalx.core.Item
        :return: guid of the item
        """
        self['item_guids'].append(item['guid'])
        return item['guid']

