from django.apps import apps

from django.db import models, transaction
from django.db.models import Q

from django.db.models.fields.related import OneToOneField, OneToOneRel
from django.db.models.fields.related import ManyToManyField, ManyToManyRel
from django.db.models.fields.related import ManyToOneRel
from django.db.models.fields.related import ForeignKey

# from django.db.models.fields.related_descriptors import \
#     ReverseOneToOneDescriptor, ReverseManyToOneDescriptor

from .utils.adapter_base import AdapterBase
from .utils.column_type import ColumnType
from .utils.relation_type import RelationType


#--- start debug tool ----------------------------------------------------------
from django.db import connection
from functools import wraps

class _DebugQueries(object):
    
    def start(self):
        self.start_query_count = len(connection.queries)
        
    def end(self):
        print('+'*100)
        for i, q in enumerate(connection.queries[self.start_query_count:]):
            print('-'*80)
            print(i, q['sql'])
        print('*'*100)
        
    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()

dq = _DebugQueries()

def _dq_decorator(func):
    @wraps
    def dq_decorated(self, *args, **kwargs):
        global dq
        with dq:
            return func(self, *args, **kwargs)
            
    return dq_decorated
#--- end debug tool ------------------------------------------------------------        


class DjangoAdapter(AdapterBase):
    """ An adapter for working with Django ORM.
    
    The `adapter_settings` is a dictionary with next values:
    
        - *using* is a database name (a key from `DATABASES` dictionary in the
          "settings.py" file of a Django project), if it isn't provided
          "default" database is used.
    
    .. note::
    
        If you are going to use transactions provided by this library,
        set `autocommit` for the database to `False`:
        
            .. code-block:: Python
        
                from django.db import transaction
                from save_to_db import Persister
                from save_to_db.adapters import DjangoAdapter
                
                persister = Persister(DjangoAdapter, adapter_settings={})
                
                # Next function takes a `using` argument which should be the
                # name of a database. If it isn’t provided, Django uses the
                # "default" database.
                transaction.set_autocommit(False, using='database_name')
                
                try:
                    persister.persist(save_to_db_item)
                    persister.commit()
                except:
                    persister.rollback()
        
        Alternativy, you can use Django transactions directly:
        
            .. code-block:: Python
            
                from django.db import transaction
                from save_to_db import Persister
                from save_to_db.adapters import DjangoAdapter
                
                persister = Persister(DjangoAdapter, adapter_settings={})
                
                with transaction.atomic():
                    persister.persist(save_to_db_item)
    """
    
    COMPOSITE_KEYS_SUPPORTED = False
    REVERSE_MODEL_AUTOUPDATE_SUPPORTED = False
    SAVE_MODEL_BEFORE_COMMIT = True
    
    
    #--- general methods -------------------------------------------------------
    
    @classmethod
    def is_usable(cls, model_cls):
        return issubclass(model_cls, models.Model)
    
    
    @classmethod
    def commit(cls, adapter_settings):
        transaction.commit(using=adapter_settings.get('using', 'default'))


    @classmethod
    def rollback(cls, adapter_settings):
        transaction.rollback(using=adapter_settings.get('using', 'default'))
    
    
    @classmethod
    def iter_fields(cls, model_cls):
        foreign_key_classes = (ForeignKey, ManyToOneRel,
                               OneToOneField, OneToOneRel,
                               ManyToManyField, ManyToManyRel)
        
        type_to_const = (
            (models.BinaryField, ColumnType.BINARY),
            (models.TextField, ColumnType.TEXT),
            (models.CharField, ColumnType.STRING),
            ((models.AutoField, models.IntegerField), ColumnType.INTEGER),
            ((models.BooleanField,
              models.NullBooleanField), ColumnType.BOOLEAN),
            (models.DateTimeField, ColumnType.DATETIME),
            ((models.FloatField,
              models.DecimalField), ColumnType.FLOAT),
            (models.DateField, ColumnType.DATE),
            (models.TimeField, ColumnType.TIME),
            (models.DateTimeField, ColumnType.DATETIME),
        )
        for field in model_cls._meta.get_fields():
            if isinstance(field, foreign_key_classes):
                continue
            
            yield_type = ColumnType.OTHER
            for field_class, column_type in type_to_const:
                if isinstance(field, field_class):
                    yield_type = column_type
                    break
            yield field.name, yield_type
    
    
    @classmethod
    def iter_relations(cls, model_cls):
        foreign_key_classes = (ForeignKey, ManyToOneRel,
                               OneToOneField, OneToOneRel,
                               ManyToManyField, ManyToManyRel)
        
        type_to_const = [
            [(OneToOneField, OneToOneRel), RelationType.ONE_TO_ONE],
            [ForeignKey, RelationType.MANY_TO_ONE],
            [ManyToOneRel, RelationType.ONE_TO_MANY],
            [(ManyToManyField,
              ManyToManyRel), RelationType.MANY_TO_MANY],
        ]
        for field in model_cls._meta.get_fields():
            if not isinstance(field, foreign_key_classes):
                continue
            
            for field_class, column_type in type_to_const:
                if isinstance(field, field_class):
                    yield_type = column_type
                    break
            
            field_name = field.name
            if hasattr(field, 'get_accessor_name'):
                field_name = field.get_accessor_name()
            
            remote_field_name = None
            if not hasattr(field.remote_field, 'is_hidden') or \
                    not field.remote_field.is_hidden():
                remote_field_name = field.remote_field.name
                if hasattr(field.remote_field, 'get_accessor_name'):
                    remote_field_name = field.remote_field.get_accessor_name()
            
            yield field_name, field.related_model, yield_type, \
                remote_field_name
    
    
    @classmethod
    def iter_required_fields(cls, model_cls):
        for field in model_cls._meta.get_fields():
            if isinstance(field, (models.AutoField, ManyToManyField)):
                continue
            if not field.null and field.default is models.NOT_PROVIDED:
                yield field.name
    
    
    @classmethod
    def iter_unique_field_combinations(cls, model_cls):
        for unique_constraint_fields in model_cls._meta.unique_together:
            yield unique_constraint_fields
            
        for field in model_cls._meta.get_fields():
            if hasattr(field, 'field'):  # relation
                if isinstance(field, (OneToOneField,
                                      OneToOneRel)):
                    yield {field.name,}  # one-to-one always unique
                    continue
                field = field.field
            if field.unique:
                yield {field.name,}
    
    
    @classmethod
    def get_table_fullname(cls, model_cls):
        return model_cls._meta.db_table
    
    
    @classmethod
    def get_model_cls_by_table_fullname(cls, name, adapter_settings):
        for models in apps.all_models.values():
            for model in models.values():
                if cls.get_table_fullname(model) == name:
                    return model
    
    
    #--- methods for working with items ----------------------------------------
    
    @classmethod
    def get(cls, items_and_fkeys, adapter_settings):
        using = adapter_settings.get('using', 'default')
        
        #--- first getting item models from database ---------------------------
        if not items_and_fkeys:
            return []
        
        all_items_filters = Q()
        getters = items_and_fkeys[0][0].getters
        
        for item, fkeys in items_and_fkeys:
            one_item_filters = Q()
            for group in getters:
                group_filters = Q()
                skip_group_filters = False
                # in case related item was not in database
                for field_name in group:
                    if field_name not in item or \
                            item[field_name] is None:
                        skip_group_filters = True
                        break
                    
                    if field_name in item.fields:
                        field_value = item[field_name]
                        group_filters &= Q(**{field_name: field_value})
                    elif field_name in item.relations:
                        related_models = fkeys.get(field_name)
                        if not related_models:
                            # failed to get or created related model before
                            skip_group_filters = True
                            break
                        
                        relation = item.relations[field_name]
                        if not relation['relation_type'].is_x_to_many():
                            group_filters &= Q(
                                **{field_name: related_models[0]})
                        else:
                            contains_any = Q()
                            for related_model in related_models:
                                contains_any |= Q(**{field_name: related_model})
                            group_filters &= contains_any
                
                if not skip_group_filters and len(group_filters):
                    one_item_filters |= group_filters
                
            if one_item_filters.children:
                all_items_filters |= one_item_filters
        
        if not len(all_items_filters):
            return []
            
        return item.model_cls.objects.db_manager(using) \
            .filter(all_items_filters).all()
    
    @classmethod
    def create_blank_model(cls, model_cls, adapter_settings):
        return model_cls()
    
    @classmethod
    def add_related_models(cls, model, fkey, related_models):
        getattr(model, fkey).add(*related_models)
                
    @classmethod
    def clear_related_models(cls, model, fkey):
        getattr(model, fkey).clear()
        
    @classmethod
    def related_x_to_many_exists(cls, model, fkey, adapter_settings):
        return getattr(model, fkey).exists()
    
    @classmethod
    def related_x_to_many_contains(cls, model, fkey, child_models,
                                   adapter_settings):
        if not child_models:
            return []
        
        # no composite PK in Django
        pk_name = cls.get_primary_key_names(model)[0]
        pk_list = [getattr(child_model, pk_name)
                   for child_model in child_models]
        contained_models = getattr(model, fkey).filter(**{
            '{}__in'.format(pk_name): pk_list
        })
        result = []
        for contained_model in contained_models:
            for child_model in child_models:
                if child_model == contained_model:
                    result.append(child_model)
                    break
                
        return result
    
    @classmethod
    def get_primary_key_names(cls, model_cls):
        return (model_cls._meta.pk.name,)
    
    @classmethod
    def save_model(cls, model, adapter_settings):
        using = adapter_settings.get('using', 'default')
        try:
            model.save(using=using)
        except:
            cls.pprint(model)
            raise
        
    #--- methods for tests -----------------------------------------------------
    
    @staticmethod
    def get_all_models(model_cls, adapter_settings, sort_key=None):
        models = list(model_cls.objects.db_manager(
            adapter_settings.get('using', 'default')).all())
        if sort_key:
            models.sort(key=sort_key)
        return models
    
    @classmethod
    def get_related_x_to_many(cls, model, fkey, sort_key=None):
        models = list(getattr(model, fkey).all())
        if sort_key:
            models.sort(key=sort_key)
        return models