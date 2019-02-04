import pprint


class DictWrapper(dict):
    """ Used as a temporary wrapper around
    :py:class:`~save_to_db.core.item_base.ItemBase` instance for compatibility
    with Scrapy project.
    
    Scrapy is an open source and collaborative framework for extracting the data
    you need from websites. In a fast, simple, yet extensible way.
    [#DictWrapper_1]_
    
    .. [#DictWrapper_1] Citation from https://scrapy.org site.

    When parsing a page with Scrapy you cannot yield instances of arbitrary
    classes, but you can yield an instance of a `dict` class which is treated
    as an instance of a Scrapy item and properly sent to item pipelines.
    
    Using :py:meth:`~save_to_db.core.item_base.ItemBase.to_dict` and then
    :py:meth:`~save_to_db.core.item_base.ItemBase.load_dict` of
    :py:class:`~save_to_db.core.item_base.ItemBase` instance is expensive, as it
    properly transforms an item into a `dict` and then `dict` to item. Using
    :py:meth:`~save_to_db.core.item_base.ItemBase.dict_wrapper` method of
    :py:class:`~save_to_db.core.item_base.ItemBase` will just wrap an item in
    a :py:class:`~.DictWrapper` instance (subclass of `dict` class),
    later you can get the wrapped item from the wrapper in a Scrapy pipeline. 
    
    Instances of Scrapy items and of this library items are not completely
    compatible, so you need to use different item pipelines for this library
    items, the pipelines must accept and return instances of
    :py:class:`~.DictWrapper` if you want to use more then one pipeline.
    
    Here is an example of a Scrapy pipeline that saves items to a database:
    
        .. code-block:: Python
        
            from django.db import transaction
            from save_to_db import Persister
            from save_to_db.adapters import DjangoAdapter

            persister = Persister(DjangoAdapter, adapter_settings={})

            class DbPipeline(object):
            
                def process_item(self, item, spider):
                    stdb_item = item.get_item()
                    
                    with transaction.atomic():
                        persister.persist(stdb_item)
                    
                    return item  # returning item wrapper
                    
        .. note:
            Printing item wrapper to a console will output the wrapped item
            as a dictionary.  
    
    
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