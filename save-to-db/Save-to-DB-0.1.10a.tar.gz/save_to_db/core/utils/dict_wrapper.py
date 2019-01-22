import pprint


class DictWrapper(dict):
    """ Used as a temporary wrapper around
    :py:class:`~save_to_db.core.item_base.ItemBase` instance for compatibility
    with Scrapy project.
    
    Scrapy is an open source and collaborative framework for extracting the data
    you need from websites. In a fast, simple, yet extensible way.
    [#DictWrapper_1]_

    When parsing a page with Scrapy you cannot yield instances of arbitrary
    classes, but you can yield an instance of a `dict` class which is treated
    as an instance of a Scrapy item. Using
    :py:meth:`~save_to_db.core.item_base.ItemBase.to_dict` and then
    :py:meth:`~save_to_db.core.item_base.ItemBase.load_dict` of
    :py:class:`~save_to_db.core.item_base.ItemBase` instance is expensive, as it
    properly transforms an item into a `dict` and then `dict` to item. Using
    :py:meth:`~save_to_db.core.item_base.ItemBase.dict_wrapper` method of
    :py:class:`~save_to_db.core.item_base.ItemBase` will just wrap an item in
    an `DictWrapper` instance (subclass of `dict` class),
    later you can get the wrapped item from the wrapper in a Scrapy pipeline. 
    
    .. [#DictWrapper_1] Citation from https://scrapy.org site.
    
    :param item: An instance of :py:class:`~save_to_db.core.item_base.ItemBase`
        to be wrapped in a dictionary.
    """
    
    def __init__(self, item):
        self['item'] = item
    
    def get_item(self):
        """ Returns an originally wrapped item instance.
        
        :returns: Instance of
            :py:class:`~save_to_db.core.item_base.ItemBase` class.
        """
        return self['item']
    
    def __str__(self):
        return pprint.pformat(self.get_item().to_dict())