from save_to_db.core.exceptions.scope_except import ItemClsAlreadyScoped
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
        
        scope = Scope(fixes={
                self.ItemGeneralOne: {
                    'conversions': {
                        'date_format': new_date_format,
                    }
                }
            })
        self.assertEqual(len(scope._classes), 2)  # only 2 items scoped
        
        ScopedTypes, ScopedGeneralOne, ScopedGeneralTwo = \
            scope.get(self.ItemFieldTypes,
                      self.ItemGeneralOne,
                      self.ItemGeneralTwo)
        
        # no references to the scoped item, original returned
        self.assertIs(ScopedTypes, self.ItemFieldTypes)
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
    
    
    def test_default_item_cls(self):
        default_date_format = \
            self.ItemGeneralOne.conversions['date_format']
            
        new_date_format = '%d.%m.%Y'
        self.assertNotEqual(new_date_format, default_date_format)
        
        new_default_date_format = '%m/%d/%Y'
        self.assertNotEqual(new_default_date_format, default_date_format)
        
        scope = Scope(fixes={
                self.ItemGeneralOne: {
                    'conversions': {
                        'date_format': new_date_format,
                    }
                },
                None: {
                    'conversions': {
                        'date_format': new_default_date_format,
                    }
                }
            })
        self.assertEqual(len(scope._classes), 3)  # all items scoped
        
        ScopedTypes, ScopedGeneralOne, ScopedGeneralTwo = \
            scope.get(self.ItemFieldTypes,
                      self.ItemGeneralOne,
                      self.ItemGeneralTwo)
        
        # checking returned items
        expected = {
            # scoped
            ScopedTypes: new_default_date_format,
            ScopedGeneralOne: new_date_format,  # changed directly
            ScopedGeneralTwo: new_default_date_format,
            
            self.ItemFieldTypes: default_date_format,
            self.ItemGeneralOne: default_date_format,
            self.ItemGeneralTwo: default_date_format,
        }
        for item_cls, expected_date_format in expected.items():
            actual_date_format = item_cls.conversions['date_format']
            self.assertEqual(actual_date_format, expected_date_format)
            
    
    def test_item_already_scoped_exception(self):
        scope = Scope(fixes={
                self.ItemFieldTypes: {
                    'conversions': {
                        'date_format': '%m/%d/%Y',
                    }
                },
            })
        ScopedTypes = scope.get(self.ItemFieldTypes)[0]
        
        with self.assertRaises(ItemClsAlreadyScoped):
            scope = Scope(fixes={
                    ScopedTypes: {
                        'conversions': {
                            'date_format': '%d-%m-%Y',
                        }
                    },
                })
    
    
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
        
        scope = Scope(fixes={
                ItemGeneralOne: {
                    'conversions': {
                        'date_format': new_date_format,
                    }
                },
            })
        
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
        
    
    def test_item_cls_autogeneration_and_default(self):
        self.item_cls_manager.clear()
        self.item_cls_manager.autogenerate = True
        
        default_date_format = \
            self.ItemGeneralOne.conversions['date_format']
            
        new_date_format = '%m/%d/%Y'
        self.assertNotEqual(new_date_format, default_date_format)
        
        new_default_date_format = '%m/%d/%Y'
        self.assertNotEqual(new_default_date_format, default_date_format)
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
        
        scope = Scope(fixes={
                ItemGeneralOne: {
                    'conversions': {
                        'date_format': new_date_format,
                    }
                },
                None: {
                    'conversions': {
                        'date_format': new_default_date_format,
                    }
                }
            })
        
        # 1 related item was also added
        self.assertEqual(len(scope._classes), 2)
        
        ItemGeneralTwo = ItemGeneralOne.relations['two_x_x']['item_cls']
        
        self.assertTrue(ItemGeneralTwo.model_cls, self.ModelGeneralTwo)
        
        self.assertIn(ItemGeneralOne, scope._classes)
        self.assertIn(ItemGeneralTwo, scope._classes)
        
        self.assertFalse(ItemGeneralOne.metadata['autogenerated_item_cls'])
        self.assertTrue(ItemGeneralTwo.metadata['autogenerated_item_cls'])
        
        self.assertEqual(ItemGeneralOne.conversions['date_format'],
                         default_date_format)
        self.assertEqual(ItemGeneralTwo.conversions['date_format'],
                         default_date_format)
        
        self.assertEqual(scope[ItemGeneralOne].conversions['date_format'],
                         new_date_format)
        self.assertEqual(scope[ItemGeneralTwo].conversions['date_format'],
                         new_default_date_format)
        
        
        
        