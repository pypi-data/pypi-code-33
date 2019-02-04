from save_to_db.core.exceptions.scope_except import (ItemClsAlreadyScoped,
                                                     ScopeIdCannotBeNone,
                                                     ScopeIdAlreadyInUse,
                                                     ScopeDoesNotExist)
from save_to_db.core.item import Item
from save_to_db.core.scope import Scope
from save_to_db.utils.test_base import TestBase



class TestScope(TestBase):
    
    ModelFieldTypes = None
    ModelGeneralOne = None
    ModelGeneralTwo = None
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        class ItemFieldTypes(Item):
            model_cls = cls.ModelFieldTypes
        
        class ItemGeneralOne(Item):
            model_cls = cls.ModelGeneralOne
                
        class ItemGeneralTwo(Item):
            model_cls = cls.ModelGeneralTwo
        
        cls.ItemFieldTypes = ItemFieldTypes
        cls.ItemGeneralOne = ItemGeneralOne
        cls.ItemGeneralTwo = ItemGeneralTwo
    
    def test_relation_replacement(self):
        default_date_format = \
            self.ItemGeneralOne.conversions['date_format']
            
        new_date_format = '%d.%m.%Y'
        self.assertNotEqual(new_date_format, default_date_format)
        
        scope = Scope(
            fixes={
                self.ItemGeneralOne: {
                    'conversions': {
                        'date_format': new_date_format,
                    }
                }
            },
            scope_id='test_relation_replacement')
        self.assertEqual(len(scope._classes), 2)  # only 2 items scoped
        
        ScopedTypes, ScopedGeneralOne, ScopedGeneralTwo = \
            scope.get(self.ItemFieldTypes,
                      self.ItemGeneralOne,
                      self.ItemGeneralTwo)
        
        # scoped by default
        self.assertIsNot(ScopedTypes, self.ItemFieldTypes)
        # scoped directly
        self.assertIsNot(ScopedGeneralOne, self.ItemGeneralOne)
        # scoped through reference
        self.assertIsNot(ScopedGeneralTwo, self.ItemGeneralTwo)
        
        # checking returned items
        expected = {
            ScopedTypes: default_date_format,
            ScopedGeneralOne: new_date_format,  # changed
            ScopedGeneralTwo: default_date_format,
            
            self.ItemFieldTypes: default_date_format,
            self.ItemGeneralOne: default_date_format,
            self.ItemGeneralTwo: default_date_format,
        }
        for item_cls, expected_date_format in expected.items():
            actual_date_format = item_cls.conversions['date_format']
            self.assertEqual(actual_date_format, expected_date_format)

        # relations of scoped items fixed
        two_1_1_cls = ScopedGeneralOne.relations['two_1_1']['item_cls']
        self.assertIs(two_1_1_cls, ScopedGeneralTwo)
        
        one_x_x_cls = ScopedGeneralTwo.relations['one_x_x']['item_cls']
        self.assertIs(one_x_x_cls, ScopedGeneralOne)
        
        # relations of not scoped items left as they were
        two_1_1_cls = \
            self.ItemGeneralOne.relations['two_1_1']['item_cls']
        self.assertIs(two_1_1_cls, self.ItemGeneralTwo)
        
        one_x_x_cls = \
            self.ItemGeneralTwo.relations['one_x_x']['item_cls']
        self.assertIs(one_x_x_cls, self.ItemGeneralOne)
    
    
    def test_none_and_true_item_cls(self):
        scope = Scope(
            fixes={
                self.ItemGeneralOne: {
                    'update_only_mode': True,
                },
                None: {
                    'allow_merge_items': True
                },
                True: {
                    'allow_multi_update': True,
                }
            },
            scope_id='test_none_and_true_item_cls')
        self.assertEqual(len(scope._classes), 3)  # all items scoped
        
        defaults = {
            'update_only_mode': False,
            'allow_merge_items': False,
            'allow_multi_update': False,
        }
        for attr, value in defaults.items():
            for cls in [self.ItemFieldTypes,
                        self.ItemGeneralOne,
                        self.ItemGeneralTwo,]:
                self.assertEqual(getattr(cls, attr), value)
        
        ScopedTypes, ScopedGeneralOne, ScopedGeneralTwo = \
            scope.get(self.ItemFieldTypes,
                      self.ItemGeneralOne,
                      self.ItemGeneralTwo)
        
        after_scoping = {
            ScopedTypes: {
                'update_only_mode': False,
                'allow_merge_items': True,  # by `None`
                'allow_multi_update': True,  # by `True`
            },
            ScopedGeneralOne: {
                'update_only_mode': True,  # by class
                'allow_merge_items': False,
                'allow_multi_update': True,  # by `True`
            },
            ScopedGeneralTwo: {
                'update_only_mode': False,
                'allow_merge_items': True,  # by `None`
                'allow_multi_update': True,  # by `True`
            },
        }
        for scoped_cls, attrs in after_scoping.items():
            for attr, value in attrs.items():
                self.assertEqual(
                    getattr(scoped_cls, attr), value,
                    'scope: {}, cls: {}, attr: {}, val: {}'.format(
                        scoped_cls.get_scope_id(),
                        scoped_cls.__name__, attr, getattr(scoped_cls, attr)))
    
    
    def test_merging_defaults_and_conversions(self):
        self.item_cls_manager.clear()
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
                
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
        
        ItemGeneralOne.complete_setup()
        ItemGeneralTwo.complete_setup()
        
        # default_decimal_separator
        default_decimal_separator = \
            ItemGeneralOne.conversions['decimal_separator']
        # new_descimal_separator
        new_descimal_separator = '!'
        self.assertNotEqual(
            new_descimal_separator, default_decimal_separator)
        
        default_date_format = \
            self.ItemGeneralOne.conversions['date_format']
        new_date_format_true = '%d.%m.%Y'
        self.assertNotEqual(new_date_format_true, default_date_format)
        
        expected = {
            ItemGeneralOne: {
                'conversions': {
                    'decimal_separator': default_decimal_separator,
                    'date_format': default_date_format,
                },
                'defaults': {}
            },
            ItemGeneralTwo: {
                'conversions': {
                    'decimal_separator': default_decimal_separator,
                    'date_format': default_date_format,
                },
                'defaults': {}
            }
        }
        for item_cls, attrs in expected.items():
            for attr, dict_value in attrs.items():
                if not dict_value:
                    self.assertEqual(getattr(item_cls, attr), dict_value)
                    continue
                for key, value in dict_value.items():
                    self.assertEqual(
                        getattr(item_cls, attr)[key], value)
        
        # scoping
        scope = Scope(
            fixes={
                ItemGeneralOne: {
                    'defaults': {
                        'f_integer': 100,
                    },
                },
                ItemGeneralTwo: {
                    'conversions': {
                        'decimal_separator': '!',
                    },
                },
                True: {
                    'conversions': {
                        'decimal_separator': new_descimal_separator,
                        'date_format': new_date_format_true,
                    },
                    'defaults': {
                        'f_integer': 200,
                        'f_text': 'text-200',
                    },
                }
            },
            scope_id='test_merging_defaults_and_conversions')
        
        ScopedItemOne, ScopedItemTwo = scope.get(
            ItemGeneralOne, ItemGeneralTwo)
        expected = {
            ScopedItemOne: {
                'conversions': {
                    'decimal_separator': new_descimal_separator,
                    'date_format': new_date_format_true,
                },
                'defaults': {
                    'f_integer': 100,  # not overwritten
                    'f_text': 'text-200',
                }
            },
            ScopedItemTwo: {
                'conversions': {
                    'decimal_separator': '!',  # not overwritten
                    'date_format': new_date_format_true,
                },
                'defaults': {
                    'f_integer': 200,
                    'f_text': 'text-200',
                }
            }
        }
        for item_cls, attrs in expected.items():
            for attr, dict_value in attrs.items():
                if not dict_value:
                    self.assertEqual(getattr(item_cls, attr), dict_value)
                for key, value in dict_value.items():
                    self.assertEqual(
                        getattr(item_cls, attr)[key], value)
        
    
    
    def test_gen_non_scoped_cls(self):
        self.item_cls_manager.clear()
        
        class ItemFieldTypes(Item):
            model_cls = self.ModelFieldTypes
        
        scope = Scope(
            fixes={
                ItemFieldTypes: {
                    'conversions': {
                        'decimal_separator': '!',
                    }
                },
                True: {
                    'conversions': {
                        'date_format': 'TRUE: %Y-%m-%d',
                    }
                },
                None: {
                    'conversions': {
                        'datetime_format': 'NONE: %Y-%m-%d %H:%M:%S',
                    }
                }
            },
            scope_id='test_gen_non_scoped_cls')
        self.assertEqual(len(scope._classes), 1)  # only 1 items scoped
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
                
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
        
        ScopedItemOne = scope[ItemGeneralOne]
        self.assertEqual(len(scope._classes), 3)  # rest of the items scoped
        
        ScopedItemTwo = ScopedItemOne.relations['two_x_x']['item_cls']
        
        for item_cls in (ScopedItemOne, ScopedItemTwo):
            self.assertEqual(item_cls.get_scope_id(), 'test_gen_non_scoped_cls')
            conversions_two = item_cls.conversions
            
            self.assertEqual(conversions_two['date_format'],
                             'TRUE: %Y-%m-%d')
            self.assertEqual(conversions_two['datetime_format'],
                             'NONE: %Y-%m-%d %H:%M:%S')
        
    
    def test_item_already_scoped_exception(self):
        scope = Scope(
            fixes={
                self.ItemFieldTypes: {
                    'conversions': {
                        'date_format': '%m/%d/%Y',
                    }
                },
            },
            scope_id='test_item_already_scoped_exception_1')
        ScopedTypes = scope.get(self.ItemFieldTypes)[0]
        
        with self.assertRaises(ItemClsAlreadyScoped):
            scope = Scope(
                fixes={
                    ScopedTypes: {
                        'conversions': {
                            'date_format': '%d-%m-%Y',
                        }
                    },
                },
                scope_id='test_item_already_scoped_exception_2')
    
    
    def test_item_cls_autogeneration(self):
        self.item_cls_manager.clear()
        self.item_cls_manager.autogenerate = True
        
        default_date_format = \
            self.ItemGeneralOne.conversions['date_format']
        new_date_format = '%m/%d/%Y'
        self.assertNotEqual(new_date_format, default_date_format)
        
        class ItemFieldTypes(Item):
            model_cls = self.ModelFieldTypes
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
        
        scope = Scope(
            fixes={
                ItemGeneralOne: {
                    'conversions': {
                        'date_format': new_date_format,
                    }
                },
            },
            scope_id='test_item_cls_autogeneration')
        
        # 2 items including related (ItemFieldTypes discarded)
        self.assertEqual(len(scope._classes), 2)
        
        ItemGeneralTwo = ItemGeneralOne.relations['two_x_x']['item_cls']
        
        self.assertTrue(ItemGeneralTwo.model_cls, self.ModelGeneralTwo)
        
        self.assertIn(ItemGeneralOne, scope._classes)
        self.assertIn(ItemGeneralTwo, scope._classes)
        
        self.assertFalse(ItemFieldTypes.metadata['autogenerated_item_cls'])
        self.assertFalse(ItemGeneralOne.metadata['autogenerated_item_cls'])
        self.assertTrue(ItemGeneralTwo.metadata['autogenerated_item_cls'])
        
        self.assertEqual(ItemFieldTypes.conversions['date_format'],
                         default_date_format)
        self.assertEqual(ItemGeneralOne.conversions['date_format'],
                         default_date_format)
        self.assertEqual(ItemGeneralTwo.conversions['date_format'],
                         default_date_format)
        
        
        self.assertEqual(scope[ItemFieldTypes].conversions['date_format'],
                         default_date_format)
        self.assertEqual(scope[ItemGeneralOne].conversions['date_format'],
                         new_date_format)
        self.assertEqual(scope[ItemGeneralTwo].conversions['date_format'],
                         default_date_format)
        
    
    def test_scope_id_cannot_be_none(self):
        with self.assertRaises(ScopeIdCannotBeNone):
            Scope(fixes={}, scope_id=None)
            
    
    def test_scope_id_already_in_use(self):
        Scope(fixes={}, scope_id='test_scope_id_already_in_use')
        
        with self.assertRaises(ScopeIdAlreadyInUse):
            Scope(fixes={}, scope_id='test_scope_id_already_in_use')
        
    
    def test_scope_does_not_exist(self):
        with self.assertRaises(ScopeDoesNotExist):
            Scope.get_scope_by_id(scope_id='test_scope_does_not_exist')
            