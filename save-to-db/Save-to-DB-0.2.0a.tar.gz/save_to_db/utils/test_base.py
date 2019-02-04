import copy
from unittest import TestCase
from save_to_db.core import signals
from save_to_db.core.item_cls_manager import item_cls_manager
from save_to_db.core.scope import Scope




class TestBase(TestCase):
    
    item_cls_manager = item_cls_manager
    
    @classmethod
    def setUpClass(cls):
        cls.item_cls_manager.clear()
        Scope.scopes.clear()
        super().setUpClass()
        
        
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Scope.scopes.clear()
    
    
    def setUp(self):
        self.item_cls_manager.autogenerate = False
        self.__item_cls_manager_before = \
            set(self.__class__.item_cls_manager._registry)
        self.__scopes_before = copy.deepcopy(Scope.scopes)
        super().setUp()
        
    
    def tearDown(self):
        super().tearDown()
        self.__class__.item_cls_manager._registry = \
            self.__item_cls_manager_before
        Scope.scopes = self.__scopes_before
        for signal in signals.all_signals:
            signal.clear()
        
    
    
    def get_all_models(self, model_cls, sort_key=None):
        adapter_settings = self.persister.adapter_settings
        adapter_cls = self.persister.adapter_cls
        return adapter_cls.get_all_models(model_cls,
                                          adapter_settings=adapter_settings,
                                          sort_key=sort_key)
        
    def get_related_x_to_many(self, model_cls, field_name, sort_key=None):
        adapter_cls = self.persister.adapter_cls
        return adapter_cls.get_related_x_to_many(model_cls, field_name,
                                                 sort_key=sort_key)
