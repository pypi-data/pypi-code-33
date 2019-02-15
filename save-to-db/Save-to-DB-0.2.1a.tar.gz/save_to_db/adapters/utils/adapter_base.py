from itertools import chain
from .db_persister import db_persist


class AdapterBase(object):
    """ Base adapter class for all database adapters.
    Here you can see descriptions of all required methods for DB adapters
    that are going to extend this class.
    """

    #: Must be set to `True` if ORM supports composite primary keys.
    COMPOSITE_KEYS_SUPPORTED = True
    
    #: Must be set to `True` if ORM automatically updates model that is being
    #: assigned to or unassigned from another model.
    REVERSE_MODEL_AUTOUPDATE_SUPPORTED = True
    
    #: This value must be set to `True` if a model has to be first saved
    #: before its changes can be committed to database. 
    SAVE_MODEL_BEFORE_COMMIT = False
    
    #: Maximum number of models that can be pulled with one query.
    #:
    #:     .. seealso::
    #:        `batch_size` class variable of
    #:        :py:class:`~save_to_db.core.item.Item` class.
    BATCH_SIZE = 300
    
    #--- general methods -------------------------------------------------------
    
    @classmethod
    def is_usable(cls, model_cls):
        """ Returns `True` if this adapter can deal with `model_cls` class.
        Here you must somehow recognize that the model class was created
        using the particular ORM library that this adapter is for.
        
        :param model_cls: ORM model class (of any library).
        :returns: Boolean value indicating whether this adapter can deal with
            the given model class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def commit(cls, adapter_settings):
        """ Commits current transaction to database.
        
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def rollback(cls, adapter_settings):
        """ Rolls back current transaction.
        
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def iter_fields(cls, model_cls):
        """ Returns an iterator of field names and their types. Foreign keys
        and relations must be ignored.
        
        :param model_cls: ORM model class for which column data are going to be
            returned.
        :returns: A generator of tuples of type:
        
                *(field_name, field_type)*
            
            Where:
            
                - *field_name* is a name of an ORM model field.
                - *field_type* must be one of the fields of
                  :py:class:`~.column_type.ColumnType` enumeration class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def iter_relations(cls, model_cls):
        """ Returns an iterator of all fields that used to reference other
        ORM models.
        
        :param model_cls: ORM model class for which relations are going to be
            iterated.
        :returns: A generator of tuples of type:
        
                *(relation_field_name, relation_model_cls, relation_type,
                reverse_key)*
                
            Where:
            
            - *relation_field_name* is a field of the `model_cls` that
              references another model.
            
            - *relation_model_cls* is an ORM model class being referenced.
              
            - *relation_type* must be one of the fields of
              :py:class:`~.relation_type.RelationType` enumeration class.
            
            - *reverse_key* is the relationship name used in related model
              to reference the original model.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def iter_required_fields(cls, model_cls):
        """ Returns an iterator of fields that cannot be null for an ORM model
        class:
        
            - Simple field value cannot be null if the column has a not null
              constraint.
            - Relation field cannot be null if any column used as
              foreign key (can be multiple in case of composite key) is not
              null.
        
        :param model_cls: ORM model class for which relations are going to be
            iterated.
        :returns: A generator of field names.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def iter_unique_field_combinations(cls, model_cls):
        """ Returns an iterator of unique fields.
        
        .. note::
            Relation considered to be unique if the set of columns used as
            foreign keys (can be multiple in case of composite key) has a
            unique constraint.
        
            *Relations can be unique together with other fields.*
        
        :param model_cls: ORM model class for which relations are going to be
            iterated.
        :returns: A generator of field names.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def get_table_fullname(cls, model_cls):
        """ Returns full table name with schema (if applicable) used by an
        ORM model class.
        
        :param model_cls: An ORM model class.
        :returns: Full table name with schema (if applicable). Examples:
        
                - 'public.some_table'
                - 'some_table' (no schema, e.g. SQLite database).
        """
        raise NotImplementedError()
    
    
    @classmethod
    def get_model_cls_by_table_fullname(cls, name, adapter_settings):
        """ Return ORM model class based on full table that that model class
        uses.
        
        :param name: table full name.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        :return: ORM model class.
        """
        raise NotImplementedError()
    
    
    #--- methods for working with items ----------------------------------------
    
    @classmethod
    def persist(cls, item, adapter_settings):
        """ Saves item data into a database by creating or update appropriate
        database records.
        
        :param item: an instance of
            :py:class:`~save_to_db.core.item_base.ItemBase` to persist.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        :param commit: If `True` commits changes to database.
        :returns: Item list and corresponding ORM models as a list of lists
            (in case one item updates multiple models).
        """
        return db_persist(cls, item, adapter_settings)


    @classmethod
    def get(cls, items_and_fkeys, adapter_settings):
        """ Accepts items and their foreign keys and gets corresponding models
        from database.
        
        .. warning::
            Items must have the same ORM model class.
        
        :param items_and_fkeys: a list of lists of type:
        
            .. code-block:: Python
            
                [
                    [item, {fkey: model, ...}],
                    ...
                ]
                
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        :returns: List of created and updated models.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def create_blank_model(cls, model_cls, adapter_settings):
        """ Create empty model instance.
        
        :param model_cls: ORM model class to create.
        :returns: Newly created ORM model instance.
        """
        raise NotImplementedError()
    
    @classmethod
    def add_related_models(cls, model, fkey, related_models):
        """ Adds related models for x-to-many relationships to a parent model.
        
        :param model: Parent ORM model instance.
        :param key: Parent ORM model instance foreign key field.
        :param related_models: Referenced ORM models.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def clear_related_models(cls, model, fkey):
        """ Removes related models for x-to-many relationships from a parent
        model.
        
        :param model: Parent ORM model instance.
        :param fkey: Parent ORM model instance foreign key field.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def related_x_to_many_exists(cls, model, fkey, adapter_settings):
        """ Returns `True` if `model` contains any other models with
        `field_name` relation key.
        
        :param model: Parent ORM model instance.
        :param fkey: Parent ORM model instance foreign key field.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        :returns: `True` if `model` contains any other models with
            the relation key.
        """
        raise NotImplementedError()
    
    @classmethod
    def related_x_to_many_contains(cls, model, fkey, child_models,
                                   adapter_settings):
        """ Returns list of contained models from `child_models` by
        `model` parent model trough `field_name` foreign key field.
        
        .. note::
            The returned list must contain instances from `child_models` list,
            not other instances for the same database rows.
        
        :param model: ORM model instance.
        :param fkey: field name used for reference.
        :param child_models: list of child models.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        :returns: Returns list of contained models from `child_models` by
            `model` parent model trough `fkey` foreign key field.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def get_primary_key_names(cls, model_cls):
        """ Returns tuple of primary key names.
        
        :param model_cls: ORM model class.
        :returns: Tuple of primary key names of `model_cls`.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def save_model(self, model, adapter_settings):
        """ Saves ORM model to database.
        
        .. note::
            If possible, session must not be committed, just flushed.
        
        :param model: Parent ORM model instance.
        :param key: Parent ORM model instance foreign key field.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        """
        raise NotImplementedError()
    

    #--- helper functions ------------------------------------------------------
    
    @classmethod
    def pprint(cls, *models):
        """ Pretty prints `models`.
        
        :param \*models: List of models to print.
        """
        if not models:
            return
        
        def repr_model(model):
            pkeys_names = cls.get_primary_key_names(model.__class__)
            pkeys_values = list(str(getattr(model, pkey))
                                for pkey in pkeys_names)
            return '({},)'.format(','.join(pkeys_values))
            
        
        model_cls = None
        for model in models:
            if not (model.__class__ is model_cls):
                model_cls = model.__class__
                pkeys_names = cls.get_primary_key_names(model_cls)
        
                field_names = [
                    fname for fname, _, in cls.iter_fields(model_cls)
                ]
                for pk_fname in pkeys_names:
                    field_names.remove(pk_fname)
                field_names.sort()
                
                relations = {
                    fname: direction
                    for fname, _, direction, _ in cls.iter_relations(model_cls)
                }
                relation_names = list(relations.keys())
                relation_names.sort()
                
                padding = len(max(chain(pkeys_names,
                                        field_names,
                                        relation_names), key=len))
                
            to_print = ['{}:'.format(model_cls.__name__)]
            for fname in chain(pkeys_names, field_names, relation_names):
                if fname in field_names or fname in pkeys_names:
                    value = getattr(model, fname)
                    no_value = value is None
                else:
                    if not relations[fname].is_x_to_many():
                        other_model = None
                        if hasattr(model, fname):
                            other_model = getattr(model, fname)
                            
                        if other_model is None:
                            value = None
                            no_value = True
                        else:
                            value = repr_model(other_model)
                            no_value = False
                    else:
                        other_models = cls.get_related_x_to_many(model, fname)
                        no_value = not other_models
                        value = '[{}]'.format(
                            ','.join([repr_model(m) for m in other_models]))
                    
                to_print.append('    {:<3} {:>{padding}}: {}'.format(
                    'PK' if fname in pkeys_names else
                        '' if no_value else '::',
                    fname if no_value else fname.upper(),
                    value,
                    padding=padding))
            
            print('\n'.join(to_print))
    
    
    #--- methods for tests -----------------------------------------------------
    
    @staticmethod
    def get_all_models(model_cls, adapter_settings, sort_key=None):
        """ Returns all models from database `model_cls` class.
        
        .. note::
            Used by tests only.
        
        :param model_cls: An ORM model class.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        :param sort_key: If not `None` then result is sorted using this
            function as `key` argument for `sort` method of the result list.
        :returns: List of all model instances for `model_cls` class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def get_related_x_to_many(cls, model, fkey, sort_key=None):
        """ Returns list of many-to-many related  models.
        
        .. note::
            Used by tests only.
        
        :param model: ORM model instance.
        :param fkey: field name used for reference.
        :param sort_key: If not `None` then result is sorted using this
            function as `key` argument for `sort` method of the result list.
        :returns: List of many-to-many related models.
        """
        result = list(getattr(model, fkey))
        if sort_key:
            result.sort(key=sort_key)
        return result