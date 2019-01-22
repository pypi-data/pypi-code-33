import pickle
import struct
from .item_cls_manager import item_cls_manager



class Persister(object):
    """ This class is used to persist items to database or save and load them
    from files.
    
    :param adapter_cls: Subclass of
        :py:class:`~save_to_db.adapters.utils.adapter_base.AdapterBase` used
        to deal with items and ORM models.
    :param adapter_settings: Adapter configuration object. This parameter is
        unique for each adapter class.
    :param autocommit: If `True` commits changes to database each time an
        item is persisted.
    """
    
    def __init__(self, adapter_cls, adapter_settings, autocommit=False):
        self.adapter_cls = adapter_cls
        self.adapter_settings = adapter_settings
        self.autocommit = autocommit
    
    
    #--- database adapter facade -----------------------------------------------
    
    def persist(self, item, commit=None):
        """ Saves item data into a database by creating or update appropriate
        database records.
        
        :param item: an instance of :py:class:`~.item_base.ItemBase` to persist.
        :param commit: If `True` commits changes to database. If `None` then
            `autocommit` value (initially set at creation time) is used.
            
            .. note::
                In case of exception, in case transaction would normally be
                committed, this method rolls back the transaction.
            
        :returns: Item list and corresponding list of ORM  model lists.
        """
        try:
            result = self.adapter_cls.persist(item, self.adapter_settings)
            if commit or (commit is None and self.autocommit):
                self.commit()
            return result
        except:
            if commit or (commit is None and self.autocommit):
                self.rollback()
            raise
        
        

    def commit(self):
        """ Commits persisted items to database. """
        self.adapter_cls.commit(self.adapter_settings)
    
    
    def rollback(self):
        """ Rolls back current transaction. """
        self.adapter_cls.rollback(self.adapter_settings)
        
    
    def pprint(self, *models):
        """ Pretty prints `model` to console.
        
        :param \*models: List of models to print.
        """
        self.adapter_cls.pprint(*models)
    
    
    #--- interface for working with files --------------------------------------
    
    def dumps(self, item):
        """ Converts an item into bytes.
        
        :param item: An instance of :py:class:`~.item_base.ItemBase` class.
        :returns: Encoded item as `bytes`.
        """
        item.process()
        model_cls = item.model_cls
        return pickle.dumps({
            'table_fullname': self.adapter_cls.get_table_fullname(model_cls),
            'is_bulk_item': item.is_bulk_item(),
            'dict_wrapper': item.to_dict(),
        })
    
    
    def loads(self, data):
        """ Decodes `bytes` data into an instance of
        :py:class:`~.item_base.ItemBase`.
        
        :param data: Encoded item as `bytes`.
        :returns: An instance of :py:class:`~.item_base.ItemBase`.
        """
        result_data = pickle.loads(data)
        
        model_cls = self.adapter_cls.get_model_cls_by_table_fullname(
            result_data['table_fullname'], self.adapter_settings)
        item_cls = item_cls_manager.get_by_model_cls(model_cls)[0]
        
        item = item_cls.Bulk() if result_data['is_bulk_item'] else item_cls()
        item = item.load_dict(result_data['dict_wrapper'])
        
        return item
    
        
    def dump(self, item, fp):
        """ Saves an item into a file.
        
        .. note::
            This method also saves the size of encoded item. So it is possible
            to save multiple items one after another into the same file and
            load them later.
        
        :param item: An item to be saved.
        :param fp: File-like object to save `item` into.
        """
        item_data = self.dumps(item)
        fp.write(struct.pack('>I', len(item_data)))
        fp.write(item_data)
        
    
    def load(self, fp):
        """ Loads and decodes one item from a file-like object.
        
        :param fp: File-like object to read from.
        :return: One item read from `fp` or `None` if there are no data to read
            anymore.
        """
        int_as_bytes = fp.read(4)
        if not int_as_bytes:
            return None
        l = struct.unpack('>I', int_as_bytes)[0]
        return self.loads(fp.read(l))
    