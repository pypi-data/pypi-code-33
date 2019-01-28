from save_to_db.core.exceptions import (InvalidFieldName,
                                        RelatedItemNotFound,
                                        MultipleRelatedItemsFound,
                                        ItemAdapterNotFound)
from save_to_db.core.item import Item
from save_to_db.core.item_metaclass import ItemMetaclass
from save_to_db.utils.test_base import TestBase



class TestItemMetaclass(TestBase):
    """ Contains basic tests for an item metaclass.
    
    .. note:
        This test case only tests those features that can be tested without
        using any models (`model_cls` always `None`).
    """
    
    def test_conversions_overwrite(self):
        
        boolean_true_strings = ('boolean', 'true', 'strings')
        date_format = '%m/%d/%Y'
        
        class ItemA(Item):
            conversions = {
                'boolean_true_strings': boolean_true_strings,
                'date_format': date_format,
            }
        
        conversions = ItemA.conversions
        default_conversions = \
            ItemMetaclass.get_default_configuration()['conversions']
        
        # other conversions values must have been inserted
        self.assertEqual(set(conversions.keys()),
                         set(default_conversions.keys()))
        
        overwritten_conversions = {
            'boolean_true_strings': boolean_true_strings,
            'date_format': date_format,
        }
        
        for key, default_value in default_conversions.items():
            expected_value = overwritten_conversions.get(key, default_value)
            self.assertEqual(conversions[key], expected_value)
    
    
    def test_creators_getters_nullables_structure_correction(self):
        
        class ItemA(Item):
            creators = [['a', 'b'], 'c']
            getters = [['x', 'y'], 'z']
            nullables = ['e', 'f', 'g']
        
        expected_creators = [{'a', 'b'}, {'c'}]
        expected_getters = [{'x', 'y'}, {'z'}]
        expected_nullabels = {'e', 'f', 'g'}
        
        self.assertEqual(ItemA.creators, expected_creators)
        self.assertEqual(ItemA.getters, expected_getters)
        self.assertEqual(ItemA.nullables, expected_nullabels)
    
    
    def test_relations_structure_correction(self):
        
        class ItemA(Item):
            relations = {
                'item_b': 'ItemB',
                'item_c': {
                    'item_cls': 'ItemC',
                },
                'item_d': {
                    'item_cls': 'ItemD',
                    'replace_x_to_many': True,
                },
            }
        
        expected_relations = {
            'item_b': {
                'item_cls': 'ItemB',
                'relation_type': None,
                'replace_x_to_many': False,
                'reverse_key': None,
            },
            'item_c': {
                'item_cls': 'ItemC',
                'relation_type': None,
                'replace_x_to_many': False,
                'reverse_key': None,
            },
            'item_d': {
                'item_cls': 'ItemD',
                'relation_type': None,
                'replace_x_to_many': True,
                'reverse_key': None,
            },
        }
        
        self.assertEqual(ItemA.relations, expected_relations)
    
    
    def test_relations_path_replacements(self):

        #--- proper replacements ---

        class TestRelationsPathReplacements_A(Item):
            relations = {
                'item_b': 'TestRelationsPathReplacements_B',
            }
        
        class TestRelationsPathReplacements_B(Item):
            relations = {
                'item_a': {
                    'item_cls': 'TestRelationsPathReplacements_A',
                }
            }
            
        self.assertFalse(
            TestRelationsPathReplacements_A.metadata['setup_completed'])
        TestRelationsPathReplacements_A.complete_setup()
        relations = TestRelationsPathReplacements_A.relations
        self.assertIs(relations['item_b']['item_cls'],
                      TestRelationsPathReplacements_B)
        self.assertTrue(
            TestRelationsPathReplacements_A.metadata['setup_completed'])
        
        self.assertFalse(
            TestRelationsPathReplacements_B.metadata['setup_completed'])
        TestRelationsPathReplacements_B.complete_setup()
        relations = TestRelationsPathReplacements_B.relations
        self.assertIs(relations['item_a']['item_cls'],
                      TestRelationsPathReplacements_A)
        self.assertTrue(
            TestRelationsPathReplacements_B.metadata['setup_completed'])
        
        #--- related item not found ---
        
        class TestRelationsPathReplacements_C(Item):
            relations = {
                'item': 'TestRelationsPathReplacements_NONEXISTENT',
            }
        
        with self.assertRaises(RelatedItemNotFound):
            TestRelationsPathReplacements_C.complete_setup()
            
        #--- multiple related items found ---
        
        # defining item classes with the same name
        ItemRepeatedOne = type(
            'TestRelationsPathReplacements_REPEATED',
             (Item,), {})
        ItemRepeatedTwo = type('TestRelationsPathReplacements_REPEATED',
             (Item,), {})
        
        class TestRelationsPathReplacements_D(Item):
            relations = {
                    'item': 'TestRelationsPathReplacements_REPEATED',
                }
        
        # getting multiple items from the same module
        ItemRepeatedOne.__module__ = 'a.b.c'
        ItemRepeatedTwo.__module__ = 'a.b.c'
        TestRelationsPathReplacements_D.__module__ = 'a.b.c'
        with self.assertRaises(MultipleRelatedItemsFound):
            TestRelationsPathReplacements_D.complete_setup()
        
        # getting multiple items from different modules
        ItemRepeatedOne.__module__ = 'a.b.c.1'
        ItemRepeatedTwo.__module__ = 'a.b.c.2'
        with self.assertRaises(MultipleRelatedItemsFound):
            TestRelationsPathReplacements_D.complete_setup()
            
        # normal configuration with only one item in the same module and any
        # other items in other modules
        ItemRepeatedOne.__module__ = 'a.b.c'
        TestRelationsPathReplacements_D.complete_setup()
        
    
    def test_item_adapter_not_found(self):
        
        class FakeModelCls(object):
            pass
        
        class ItemA(Item):
            model_cls = FakeModelCls
                
        with self.assertRaises(ItemAdapterNotFound):
            ItemA.complete_setup()
            
    
    def test_invalid_field_name(self):
        item_configurations = [
            {
                'nullables': {'field__name'},
            },
            {
                'getters': [{'field__name'}],
            },
            {
                'creators': [{'field__name'}],
            },
            {
                'fields': {'field__name': None},
            },
            {
                'relations': {'field__name': None},
            },
            {
                'defaults': {'field__name': None},
            }
        ]
        for item_configuration in item_configurations:
            self.item_cls_manager.clear()
            InvalidItem = type('InvalidItem', (Item,), item_configuration)
            
            with self.assertRaises(InvalidFieldName):
                InvalidItem()
            