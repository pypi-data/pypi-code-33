import copy
import uuid
from .exceptions.scope_except import ItemClsAlreadyScoped
from .item_cls_manager import item_cls_manager



class Scope(object):
    """ Class for scoping :py:class:`~.item.Item` classes.
    
    :param fixes: a dictionary whose keys are item classes (or `None`
        for all classes not in the dictionary) and values are class
        attributes to be replaced.
    
    Example usage:
        
        .. code:: Python
        
            class TestItem(Item):
                model_cls = SomeModel
            
            scope = Scope({
                TestItem: {
                    'conversions': {
                        'date_format': '%m/%d/%Y',
                    },
                },
                # for items not listed
                None: {
                    'conversions': {
                        'date_format': '%d.%m.%Y',
                    },
                },
            })
            
            ScopedTestItem = scope[TestItem]  # or `scope.get(TestItem)`
    
    When an item is scoped other items that use the original item in
    relations are also scoped and their relation data fixed.
    """
    
    def __init__(self, fixes):
        self.scope_id = uuid.uuid4().int
        self._classes = {}
        item_cls_manager.autocomplete_item_classes()
        
        # fixing classes
        for item_cls, item_fixes in fixes.items():
            if item_cls is None or not item_fixes:
                continue
            self.__prepare_scoped_item_cls(item_cls, item_fixes)
        
        # default
        if None in fixes and fixes[None]:
            for item_cls in item_cls_manager._registry:
                if item_cls in self._classes:
                    continue
                self.__prepare_scoped_item_cls(item_cls, fixes[None])
        
        # fixing relations
        do_continue = True
        while do_continue:
            do_continue = False
            #--- first scoping items that need to be scoped ---
            for item_cls in item_cls_manager._registry:
                if item_cls in self._classes:
                    continue
                
                item_cls.complete_setup()
                for rel_data in item_cls.relations.values():
                    if rel_data['item_cls'] in self._classes:
                        self.__prepare_scoped_item_cls(item_cls, item_fixes={})
                        break
            
            #--- updating relations if needed ---
            for scoped_item_cls in self._classes.values():
                relations = scoped_item_cls.relations
                for key, rel_data in relations.items():
                    rel_item_cls = rel_data['item_cls']
                    if rel_item_cls not in self._classes:
                        continue
                    
                    relations[key]['item_cls'] = self._classes[rel_item_cls]
                    do_continue = True
    
    
    def __prepare_scoped_item_cls(self, item_cls, item_fixes):
        if item_cls.metadata['scope_id'] != 0:
            raise ItemClsAlreadyScoped(item_cls)
        
        item_cls.complete_setup()
        item_fixes['relations'] = copy.deepcopy(item_cls.relations)
        item_fixes['metadata'] = copy.deepcopy(item_cls.metadata)
        item_fixes['metadata']['scope_id'] = self.scope_id

        class_name = item_cls.__name__
        scoped_item_cls = type('Scoped{}'.format(class_name), (item_cls,),
                               item_fixes)
        scoped_item_cls.complete_setup()
        self._classes[item_cls] = scoped_item_cls
    
    
    def __getitem__(self, item_cls):
        if item_cls in self._classes:
            return self._classes[item_cls]
        else:
            return item_cls
    
    
    def get(self, *item_classes):
        """ Excepts non-scoped items and returns corresponding scoped items or
        original items for items not present in the scope.
        
        :param item_classes: Items for which scoped item versions going to be
            returned.
        :returns: List of scoped items. If scope does not have corresponding
            scoped version of an item class, original class is used.
        """
        return [self[item_cls] for item_cls in item_classes]
