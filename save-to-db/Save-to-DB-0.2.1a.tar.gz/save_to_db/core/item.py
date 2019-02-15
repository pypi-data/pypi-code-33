import re
from datetime import date, datetime, time
from pprint import pprint

from save_to_db.adapters.utils.column_type import ColumnType

from .item_base import ItemBase
from .item_contructor import complete_item_structure
from .item_metaclass import ItemMetaclass

from .bulk_item import BulkItem
from .exceptions import WrongAlias


#: regex for preparing strings to be converted into numeric values
_number_regex = re.compile(r'[^0-9\.]')


class Item(ItemBase, metaclass=ItemMetaclass, no_setup=True):
    """ This class is used to collect data for a single item (possibly with
    foreign keys) and then create or update corresponding rows in a database.
    
    **To configure an item class use next class variables:**
    
    :cvar model_cls: Reference to an ORM model class.
    
    :cvar batch_size: Maximum number of models that can be pulled with one
        query. Default: `None`. 
        
            .. seealso::
                `BATCH_SIZE` class constant of
                :py:class:`~save_to_db.adapters.utils.adapter_base.AdapterBase`
                class.
    
    :cvar defaults: Dictionary with default field values. Value can be
        either raw value or a callable that accepts an item as an argument
        and returns field value.
        
        .. note::
            When using default values for relations with scoping
            (see :py:class:`~.scope.Scope`), make sure that
            related items assigned by default are from the same scope, you
            can use the fact that items are automatically created when accessed:
            
            .. code-block:: Python
                
                defaults = {
                    # to make default values compatible with scoping,
                    # use this:
                    'item_1': lambda item: item['some_key](field='value')
                    # instead of this:
                    'item_2': lambda item: OtherItem(field='value')
                    # or this:
                    'item_3': OtherItem(field='value')
                }
        
    :cvar creators: List of groups (sets) of fields and
        relations, if all fields and relations from at least one group are
        set then an item can be created.
    
    :cvar autoinject_creators: If `True` (default) and creators_autoconfig
        also `True`, then for each group in creators, not null model fields will
        be added.
    
    :cvar creators_autoconfig: Sets auto configuration for `creators` fields,
        possible values:
        
            - `True` - auto configuration is on;
            - `False` - auto configuration is off;
            - `None` - auto configuration is on if `creators` was not
              configurated manually, off otherwise.
    
    :cvar getters: List of groups (sets) of fields and
        relations, if all fields and relations from at least one group are
        set then an item can be loaded from database.
    
    :cvar getters_autoconfig: Same as `creators_autoconfig` but for `getters`
        fields.
    
    :cvar nullables: Set of fields which, if a value is not set in an
        item upon saving, must be set to null or, in case of x-to-many
        relationship, the value must be set to an empty list.
        
    :cvar relations:  dictionary describing foreign keys,
        example:
            
            .. code-block:: Python
            
                relations = {
                    'one': {
                        'item_cls': ItemClassOne,
                        'replace_x_to_many': False,  # default value
                    }
                    'two': ItemClassTwo,  # if we only interested in class
                }
        
        Keys are the fields that reference other items (foreign key columns
        in database) and values are dictionaries with next keys and values:
          
            - 'item_cls' - item class used to create foreign key item;
            - 'replace_x_to_many' - Only applicable to x-to-many
              relationships. If `True` then saving item to
              database removes old values for the field from database.
              Default: `False`.
    
    :cvar aliases: A `dict` with aliases to fields and relations. Keys are
        aliases, values are fields. Keys and values can contain double
        underscores ("__").
    
    :cvar conversions: Dictionary that describes how string values must be
        converted to proper data types. Default `conversions` value:
          
        .. code-block:: Python
          
            conversions = {
                'decimal_separator': '.',
                'boolean_true_strings': ('true', 'yes', 'on', '1', '+'),
                'boolean_false_strings': ('false', 'no', 'off', '0', '-'),
                # format for dates and times used as an argument for
                # `datetime.datetime` function
                'date': '%Y-%m-%d',
                'time': '%H:%M:%S',
                'datetime': '%Y-%m-%d %H:%M:%S',
            }
        
        In case of absence of a value from `conversions` dictionary default
        value will be used.
        
    :cvar allow_multi_update: If `True` then an instance of this class can
        update multiple models. Default: `False`.
    
    :cvar allow_merge_items:
        If `True` then when dealing with items in a bulk, items that refer to
        the same in database are merged into one. Default: `False`.
    
    :cvar update_only_mode: If `True` then a new model in database will not be
        created if it does not exist. This can be an instance variable.
        Default: `False`.
        
    :cvar norewrite_fields: Dictionary with fields that should not be rewritten.
        Example:
    
        .. code-block:: Python
        
            norewrite_fields = {
                # rewrite value if it equals to`None`
                'field_1': True, 
                # never rewrite, set only when model is created  
                'field_2': False,
            }
        
        .. warning::
            Relations are not yet supported.
    """
    
    #--- special methods -------------------------------------------------------
      
    @classmethod
    def _get_real_keys(cls, key, as_string=False):
        result = []
        item_cls = cls
        
        def add_key_to_result(add_key):
            nonlocal result, item_cls
            item_cls.complete_setup()
            if add_key not in item_cls.relations and \
                    (add_key not in item_cls.fields):
                raise WrongAlias(
                    'Wrong key: {} (full path: {}), '
                    'alias of: {}'.format(add_key, key, cls))
            
            if add_key in item_cls.relations:
                item_cls = item_cls.relations[add_key]['item_cls']
                result.append(add_key)
            elif add_key in item_cls.fields:
                item_cls = None
                result.append(add_key)
            
        cur_key = key
        while cur_key:
            if item_cls is None:
                raise WrongAlias(
                    'Cannot process the rest of path: {} (full path: {}), '
                    'alias of: {}'.format(cur_key, key, cls))
            
            aliased = False
            for alias, path in item_cls.aliases.items():
                if cur_key.startswith(alias):
                    cur_key = cur_key.replace(alias, path, 1)
                    aliased = True
                    break
            if aliased:
                continue
            
            if '__' in cur_key:
                add_key, cur_key = cur_key.split('__', 1)
                add_key_to_result(add_key)
            else:
                add_key_to_result(cur_key)
                break
        
        if not as_string:
            return result
        return '__'.join(result)
    
    
    @classmethod
    def __genitem(self, key):
        """ Generates an item for the given relation key.
        
        :param key: Relation key for which to create related item instance.
        :returns: Generated item.
        """
        relation = self.relations[key]
        if relation['relation_type'].is_x_to_many():
            item = relation['item_cls'].Bulk()
        else:
            item = relation['item_cls']()
        return item
    
    
    def __setitem__(self, key, value):
        item = self
        real_keys = item._get_real_keys(key)
        for i, real_key in enumerate(real_keys[:-1]):
            if real_key not in item.data:
                item.data[real_key] = item.__genitem(real_key)
    
            item = item.data[real_key]
            if item.is_bulk_item():
                item.data['__'.join(real_keys[i+1:])] = value
                return
        
        item.data[real_keys[-1]] = value
        
        
    def __getitem__(self, key):
        result = self
        real_keys = result._get_real_keys(key)
        for i, real_key in enumerate(real_keys):
            result.complete_setup()
            
            if real_key not in result.data:
                if real_key in result.fields:
                    raise KeyError(real_key)
                result.data[real_key] = result.__genitem(real_key)
                
            result = result.data[real_key]
            if isinstance(result, BulkItem):
                bulk_real_keys = real_keys[i+1:]
                if not bulk_real_keys:
                    # return the bulk item itself
                    return result
                # something in bulk item
                return result._get_direct(bulk_real_keys)
        
        return result
    
    
    def __delitem__(self, key):
        real_keys = self._get_real_keys(key)
        item = self
        for i, real_key in enumerate(real_keys[:-1]):
            item = item.data[real_key]
            if isinstance(item, BulkItem):
                real_key = '__'.join(real_keys[i+1:])
                del item.data[real_key]
                return
            
        del item.data[real_keys[-1]]
    
    
    def __contains__(self, key):
        try:
            real_keys = self._get_real_keys(key)
        except KeyError:
            return False
        return self._contains_direct(real_keys)
    
    
    def _contains_direct(self, real_keys):
        this_key, *those_keys = real_keys
        if this_key in self.data:
            if not those_keys:
                return True
            return self.data[this_key]._contains_direct(those_keys)
        return False
    
    #--- utility methods -------------------------------------------------------
    
    def to_dict(self):
        return self._to_dict(_item_to_dict={}, _address_to_item={})
    
    
    def _to_dict(self, _item_to_dict, _address_to_item):
        self_address = id(self)
        if self_address in _item_to_dict:
            if self_address not in _address_to_item:
                _address_to_item[self_address] = len(_address_to_item) + 1
            self_id = _address_to_item[self_address]
            _item_to_dict[self_address]['id'] = self_id
            return {
                'id': self_id,
            }
        
        result = {
            'item': {},
        }
        _item_to_dict[self_address] = result
        
        # relations have to be always processed in the same order to have
        # the same value under "id" key in result dictionary each time
        data_keys = list(self.data.keys())
        data_keys.sort()
        for key in data_keys:
            value = self.data[key]
            if not isinstance(value, ItemBase):
                result['item'][key] = value
            else:
                result['item'][key] = \
                    value._to_dict(_item_to_dict=_item_to_dict,
                                   _address_to_item=_address_to_item)
        return result
    
    
    def load_dict(self, data):
        return self._load_dict(data, _id_to_item={})
    
    
    def _load_dict(self, data, _id_to_item):
        if 'id' in data:
            if data['id'] not in _id_to_item:
                _id_to_item[data['id']] = type(self)()
            
            item = _id_to_item[data['id']]
            if 'item' not in data:
                return item
        else:
            item = type(self)()
        
        for key, value in data['item'].items():
            if key in item.fields:
                item[key] = value
            elif key in item.relations:
                item[key] = item[key]._load_dict(value, _id_to_item)

        return item
    
    
    @classmethod
    def get_item_cls(cls):
        return cls
    
    @classmethod
    def is_scoped(cls):
        return cls.metadata['scope_id'] != None
    
    @classmethod
    def get_scope_id(cls):
        return cls.metadata['scope_id']
    
    
    #--- main methods ----------------------------------------------------------
    
    
    def can_create(self, fkeys):
        """ Checks that a new row can be created in database for
        the item.
        
        .. note::
            For relations fields we check that it is in `fkeys`. For normal
            fields we just check that it is present and not `None`.
        
        :param fkeys: A `dict` where keys are relation field names and values
            are ORM models that were got form or created in database.
        :returns: `True` if a corresponding row for the item can be created in
            database, `False` otherwise.
        """
        if self.creators is None or self.update_only_mode:
            return False
        if not self.creators:
            return True
        
        for group in self.creators:
            can_create = True
            for field_name in group:
                if field_name in self.relations:
                    if field_name not in fkeys:
                        can_create = False
                        break
                elif field_name not in self.data or \
                        self.data[field_name] is None:
                    can_create = False
                    break
                
            if can_create:
                return True
        return False
    
    
    @staticmethod
    def _Auto(model_cls, **kwargs):
        """ Creates new item class.
        
        :param model_cls: model for witch new item class is generated.
        :param \*\*kwargs: key-word arguments that will be used as new class
            attributes.
        :returns: Newly created item class.
        """
        kwargs['model_cls'] = model_cls
        item_cls = type('{}Item'.format(model_cls.__name__),
                        (Item,), kwargs)
        return item_cls
        
    
    @classmethod
    def Bulk(cls, *args, **kwargs):
        """ Creates a :py:class:`~.bulk_item.BulkItem` instance for this item
        class.
        
        :param \*args: Positional arguments that are passed to bulk item
            constructor.
        :param \*\*kwargs: Keyword arguments that are passed to bulk item
            constructor.
        :returns: :py:class:`~.bulk_item.BulkItem` instance for this item class.
        """
        return BulkItem(cls, *args, **kwargs)
    
    
    def as_list(self):
        return [self]
    
    
    def is_single_item(self):
        return True
    
    
    def is_bulk_item(self):
        return False
    
    
    @classmethod
    def process_field(cls, key, value, aliased=True):
        """ Converts `value` to the appropriate data type for the given
        `key`.
        
        :param key: Key using which proper value type can be determined.
            This value can contain double underscores to reference relations.
        :param value: Value to process.
        :param aliased: If it's `True` then `key` contains field aliases.
        :returns: Value converted to proper type.
        """
        cls.complete_setup()
        
        if value is None:
            return None
        
        if aliased:
            real_key = cls._get_real_keys(key, as_string=True)
        else:
            real_key = key
        
        if '__' in real_key:
            this_key, that_key = real_key.split('__', 1)
            return cls.relations[this_key]['item_cls'].process_field(
                that_key, value, aliased=False)
        
        conversions = cls.conversions
        column_type = cls.fields[real_key]
        if column_type is ColumnType.BINARY:
            if not isinstance(value, bytes):
                if isinstance(value, str):
                    value = bytes(value, 'utf-8')
                else:
                    raise ValueError('Cannot convert to bytes: {}'.format(
                        value))
        elif column_type is ColumnType.BOOLEAN:
            if not isinstance(value, bool):
                if value.lower() in conversions['boolean_true_strings']:
                    value = True
                elif value.lower() in conversions['boolean_false_strings']:
                    value = False
                else:
                    raise ValueError('Cannot convert to boolean: {}'.format(
                        value))
        elif column_type.is_str():
            if not isinstance(value, str):
                value = str(value)
        elif column_type.is_num():
            if isinstance(value, str):
                if conversions['decimal_separator'] != '.':
                    value = value.replace('.', '')
                value = value.replace(conversions['decimal_separator'], '.')
                value = _number_regex.sub('', value)
            if column_type is ColumnType.INTEGER:
                if not isinstance(value, int):
                    value = int(value)
            elif column_type is ColumnType.FLOAT:
                if not isinstance(value, float):
                    value = float(value)
        elif column_type is ColumnType.DATE:
            if not isinstance(value, date):
                value = datetime.strptime(value,
                                          conversions['date_format']).date()
        elif column_type is ColumnType.TIME:
            if not isinstance(value, time):
                value = datetime.strptime(value,
                                          conversions['time_format']).time()
        elif column_type is ColumnType.DATETIME:
            if not isinstance(value, datetime):
                value = datetime.strptime(value,
                                          conversions['datetime_format'])
        return value
    
    
    def process(self):
        self._process(_procesed_items=[])
        return complete_item_structure(self)
            
            
    def _process(self, _procesed_items):
        if self in _procesed_items:
            return
        _procesed_items.append(self)
        
        self.before_process()  # hook
        
        # processing set fields
        for key, value in self.data.items():
            if not isinstance(value, ItemBase):
                try:
                    self.data[key] = self.process_field(key, value, aliased=False)
                except:
                    raise Exception(key, value, isinstance(value, ItemBase))
            else:
                value._process(_procesed_items=_procesed_items)
        
        # processing simple defaults
        func_defaults = {}
        for key, value in self.defaults.items():
            if key in self.data:
                continue
            if hasattr(value, '__call__') and not isinstance(value, ItemBase):
                func_defaults[key] = value
                continue
            
            if key in self.fields:
                self[key] = self.process_field(key, value, aliased=False)
            else:
                value._process(_procesed_items=_procesed_items)
                self[key] = value
        
        # processing function defaults
        for key, func_default in func_defaults.items():
            value = func_default(self)
            if key in self.fields:
                self[key] = self.process_field(key, value, aliased=False)
            else:
                if not isinstance(value, list):
                    value._process(_procesed_items=_procesed_items)
                    self[key] = value
                else:
                    bulk_item = self.relations[key]['item_cls'].Bulk()
                    bulk_item.add(*value)
                    bulk_item._process(_procesed_items=_procesed_items)
                    self[key] = bulk_item
        
        # processing nullables
        for key in self.nullables:
            if key in self:
                continue
            if key in self.fields:
                self[key] = None
            elif key in self.relations:
                relation = self.relations[key]
                if relation['relation_type'].is_x_to_many():
                    self[key] = relation['item_cls'].Bulk()
                    self[key]._process(_procesed_items=_procesed_items)
                else:
                    self[key] = None
        
        self.after_process()  # hook
    
    
    #--- helper functions ------------------------------------------------------
    
    def print_config(self):
        """ Pretty prints item instance configuration to console. """
        
        default_configuration = ItemMetaclass.get_default_configuration()
        keys = list(default_configuration.keys())
        keys.sort()
        config = {}
        for key in keys:
            config[key] = getattr(self, key)
        
        pprint(config)
    
    @classmethod
    def print_cls_config(cls):
        """ Pretty prints item class configuration to console. """
        
        cls.print_config(cls)
        
        
    #--- hooks -----------------------------------------------------------------
    
    def before_process(self):
        """ A hook method that is called before processing fields values. """
        pass
    
    
    def after_process(self):
        """ A hook method that is called immediately after all fields have been
        processed.
        """
        pass
    
    
    def before_model_update(self, model):
        """ A hook method that is called before updating matching model with
        item data.
        
        :param model: Model that was pulled from database or freshly
            created (in case there were no matching models).
        """
        pass
    
    
    def after_model_save(self, model):
        """ A hook method that is called after updating matching ORM model with
        item data and saving (if needed) to a database.
        
        .. note::
            Changes are yet be committed to a database at this point.
        
        :param model: Model that was updated.
        """
        pass
    
    