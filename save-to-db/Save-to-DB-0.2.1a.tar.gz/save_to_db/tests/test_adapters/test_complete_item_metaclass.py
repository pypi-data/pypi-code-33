from save_to_db.adapters.utils.adapter_manager import get_adapter_cls
from save_to_db.adapters.utils.column_type import ColumnType
from save_to_db.adapters.utils.relation_type import RelationType
from save_to_db.core.exceptions import (
    InvalidFieldName,
    RelatedItemNotFound,
    MultipleRelatedItemsFound,
    NonExistentRelationDefined,
    NonExistentFieldUsed,
    WrongAlias,
    FieldsFromRelationNotAllowed,
    NotRewritableExceptionsAreNotYetSupported)
from save_to_db.core.item import Item
from save_to_db.utils.test_base import TestBase



class TestCompleteItemMetaclass(TestBase):
    """ Contains tests for an item metaclass that require `model_cls` attribute
    to be a proper model class.
    """
    
    # models that are needed for tests to run
    ModelFieldTypes = None
    ModelGeneralOne = None
    ModelGeneralTwo = None
    ModelInvalidFieldNames = None
    
    ModelConstraintsOne = None
    ModelConstraintsTwo = None
    ModelConstraintsThree = None
    ModelConstraintsFour = None
    ModelConstraintsFive = None
    ModelConstraintsSix = None
    ModelConstraintsSelf = None
    
    
    def setup_models(self, one=True, two=True, one_conf=None, two_conf=None,
                     clear_registry=False, complete_setup=None):
        if clear_registry:
            self.item_cls_manager.clear()
        
        if one:
            dct = {'model_cls': self.ModelGeneralOne, }
            if one_conf:
                dct.update(one_conf)
            self.ItemGeneralOne = type('ItemGeneralOne', (Item,), dct)
        if two:
            dct = {'model_cls': self.ModelGeneralTwo, }
            if two_conf:
                dct.update(two_conf)
            self.ItemGeneralTwo = type('ItemGeneralTwo', (Item,), dct)
        
        if complete_setup or (complete_setup is None and one and two):
            self.ItemGeneralOne.complete_setup()
            self.ItemGeneralTwo.complete_setup()
        
    
    def test_nonexistent_field(self):
        # proper configuration (no nonexistent fields)
        self.setup_models(
            one_conf={
                'creators': ['f_text', 'child_1_1'],  # field and relation
                'getters': ['f_float', 'parent_1_1'],
                'nullables': ['f_date', 'child_1_x'],
                'defaults': {'f_integer': None},
                'norewrite_fields': {'f_integer': True}
            },
            clear_registry=True)
        item_one_cls = self.ItemGeneralOne
        self.assertEqual(item_one_cls.creators, [{'f_text'}, {'child_1_1'}])
        self.assertEqual(item_one_cls.getters, [{'f_float'}, {'parent_1_1'}])
        self.assertEqual(item_one_cls.nullables, {'child_1_x', 'f_date'})
        self.assertEqual(item_one_cls.norewrite_fields, {'f_integer': True})
        
        # nonexistent field
        for key in ('creators', 'getters', 'nullables'):
            with self.assertRaises(NonExistentFieldUsed):
                self.setup_models(two_conf={key: ['nonexistent']},
                                  clear_registry=True)
        
        with self.assertRaises(NonExistentFieldUsed):
            self.setup_models(two_conf={'defaults': {'nonexistent': None}},
                              clear_registry=True)
        
        with self.assertRaises(NonExistentFieldUsed):
            self.setup_models(
                two_conf={
                    'norewrite_fields': {
                        'nonexistent': True
                    }
                },
                clear_registry=True)
        
        
    def test_not_rewritable_relations_are_not_yet_supported(self):
        with self.assertRaises(NotRewritableExceptionsAreNotYetSupported):
            self.setup_models(
                one_conf={
                    'norewrite_fields': {'parent_1_1': True},
                },
                clear_registry=True)
    
        
    def test_field_from_relations_not_allowed(self):
        # proper configuration (no nonexistent fields)
        self.setup_models(
            one_conf={
                'creators': ['f_text', 'child_1_1'],  # field and relation
                'getters': ['f_float', 'parent_1_1'],
                'nullables': ['f_date', 'child_1_x'],
                'defaults': {'f_integer': None},
                'norewrite_fields': {'f_integer': True},
            },
            two_conf={
                'creators': ['f_integer'],
                'getters': ['child_1_1'],
            },           
            clear_registry=True)
        item_one_cls = self.ItemGeneralOne
        item_two_cls = self.ItemGeneralTwo
        
        self.assertEqual(item_one_cls.creators, [{'f_text'}, {'child_1_1'}])
        self.assertEqual(item_one_cls.getters, [{'f_float'}, {'parent_1_1'}])
        self.assertEqual(item_one_cls.nullables, {'child_1_x', 'f_date'})
        self.assertEqual(item_one_cls.norewrite_fields, {'f_integer': True})
        
        self.assertEqual(item_two_cls.creators, [{'f_integer'}])
        self.assertEqual(item_two_cls.getters, [{'child_1_1'}])
        
         
        # field_from_relations_not_allowed
        for key in ('creators', 'getters',):
            with self.assertRaises(FieldsFromRelationNotAllowed):
                self.setup_models(two_conf={key: [{'child_1_1__f_integer'}]},
                                  clear_registry=True)
        
        for key in ('nullables',):
            with self.assertRaises(FieldsFromRelationNotAllowed):
                self.setup_models(two_conf={key: ['child_1_1__f_integer']},
                                  clear_registry=True)
        
        with self.assertRaises(FieldsFromRelationNotAllowed):
            self.setup_models(
                two_conf={
                    'defaults': {
                        'child_1_1__f_integer': None
                    }
                },
                clear_registry=True)
            
        with self.assertRaises(FieldsFromRelationNotAllowed):
            self.setup_models(
                two_conf={
                    'norewrite_fields': {
                        'child_1_1__f_integer': True
                    }
                },
                clear_registry=True)
    
    
    def test_relations_config_excpetions(self):
        # NonExistentRelationDefined
        class WithNonExistantRelation(Item):
            model_cls = self.ModelFieldTypes
            relations = {
                'non_existant': self.ModelGeneralOne,
            }

        with self.assertRaises(NonExistentRelationDefined):
            WithNonExistantRelation.complete_setup()
        
        # RelatedItemNotFound
        self.setup_models(one=True, two=False)
        with self.assertRaises(RelatedItemNotFound):
            self.ItemGeneralOne.complete_setup()
        
        # MultipleRelatedItemsFound
        self.setup_models(one=False, two=True)
        self.setup_models(one=False, two=True)  # second model
        
        with self.assertRaises(MultipleRelatedItemsFound):
            self.ItemGeneralOne.complete_setup()
        
    
    def test_fields_autoconfig(self):
        self.setup_models()
        
        extected_fields = {
            'id': ColumnType.INTEGER,
            'f_binary': ColumnType.BINARY,
            'f_boolean': ColumnType.BOOLEAN,
            'f_text': ColumnType.TEXT,
            'f_string': ColumnType.STRING,
            'f_integer': ColumnType.INTEGER,
            'f_float': ColumnType.FLOAT,
            'f_date': ColumnType.DATE,
            'f_time': ColumnType.TIME,
            'f_datetime': ColumnType.DATETIME,
        }
        self.assertEqual(self.ItemGeneralOne.fields, extected_fields)
        
    
    def test_relations_autoconfig(self):
        self.setup_models(two_conf={
            'relations': {
                    'parent_x_x': {
                        'replace_x_to_many': True,
                    },
                },
            })
        
        #--- one ---
        expected_relations = {
            'parent_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
                'reverse_key': 'child_1_1',
            },
            'child_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
                'reverse_key': 'parent_1_1',
            },
            'parent_x_1': {
                'relation_type': RelationType.MANY_TO_ONE,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
                'reverse_key': 'child_1_x',
            },
            'child_1_x': {
                'relation_type': RelationType.ONE_TO_MANY,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
                'reverse_key': 'parent_x_1',
            },
            'parent_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
                'reverse_key': 'child_x_x',
            },
            'child_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
                'reverse_key': 'parent_x_x',
            },
            'two_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
                'reverse_key': 'one_1_1',
            },
            'two_1_x': {
                'relation_type': RelationType.ONE_TO_MANY,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
                'reverse_key': 'one_x_1',
            },
            'two_x_1': {
                'relation_type': RelationType.MANY_TO_ONE,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
                'reverse_key': 'one_1_x',
            },
            'two_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
                'reverse_key': 'one_x_x',
            },
        }
        self.assertEqual(self.ItemGeneralOne.relations, expected_relations)
        
        #--- two ---
        expected_relations = {
            'parent_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
                'reverse_key': 'child_1_1',
            },
            'child_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
                'reverse_key': 'parent_1_1',
            },
            'parent_x_1': {
                'relation_type': RelationType.MANY_TO_ONE,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
                'reverse_key': 'child_1_x',
            },
            'child_1_x': {
                'relation_type': RelationType.ONE_TO_MANY,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
                'reverse_key': 'parent_x_1',
            },
            'parent_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': True,  # default overwritten
                'reverse_key': 'child_x_x',
            },
            'child_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
                'reverse_key': 'parent_x_x',
            },
            'one_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
                'reverse_key': 'two_1_1',
            },
            'one_1_x': {
                'relation_type': RelationType.ONE_TO_MANY,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
                'reverse_key': 'two_x_1',
            },
            'one_x_1': {
                'relation_type': RelationType.MANY_TO_ONE,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
                'reverse_key': 'two_1_x',
            },
            'one_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
                'reverse_key': 'two_x_x',
            },
        }
        self.assertEqual(self.ItemGeneralTwo.relations, expected_relations)
    
    
    def __to_sorted_lists(self, iterable_of_iterables):
        result = []
        for iterable in iterable_of_iterables:
            element = list(iterable)
            element.sort()
            result.append(element)
        result.sort()
        return result
    
    
    def test_creators_getter_autoconfig(self):
        # generating items for models
        models_for_items = (
            self.ModelConstraintsOne,
            self.ModelConstraintsTwo,
            self.ModelConstraintsThree,
            self.ModelConstraintsFour,
            self.ModelConstraintsFive,
            self.ModelConstraintsSix,
            self.ModelConstraintsSelf,
        )
        item_classes = []
        for model_cls in models_for_items:
            item_classes.append(type(
                model_cls.__name__.replace('Model', 'Item'), (Item,), {
                    'model_cls': model_cls
                }
            ))
            
        for item_cls in item_classes:
            item_cls.complete_setup()
        (ItemConstraintsOne, ItemConstraintsTwo, ItemConstraintsThree,
         ItemConstraintsFour, ItemConstraintsFive, ItemConstraintsSix,
         ItemConstraintsSelf) = item_classes
        
        # checking configuration
        adapter_cls = get_adapter_cls(ItemConstraintsOne.model_cls)
        composites = adapter_cls.COMPOSITE_KEYS_SUPPORTED
        
        expected = {
            ItemConstraintsOne: {
                'creators': [{'f_text', 'f_string'}],
                'getters': [{'id'}, {'f_integer'}, {'f_string'}, {'five_1_1'}],
            },
            ItemConstraintsTwo: {
                'creators': [{'four_x_1'}],
                'getters': [{'id'}],
            },
            ItemConstraintsThree: {
                'creators': [{'one_x_1'}],
                'getters': [{'id'}],
            },
            ItemConstraintsFour: {
                'creators':
                    [{'primary_two', 'primary_one'}]
                        if composites else [],
                'getters':
                    [{'primary_two', 'primary_one'} if composites else {'id'},
                     {'five_1_1'}, {'f_integer', 'f_string'}],
            },
            ItemConstraintsFive: {
                'creators': [],
                'getters': [{'id'}, {'one_1_1'}, {'four_1_1'}, {'six_1_1'}],
            },
            ItemConstraintsSix: {
                'creators': [{'five_1_1'}],
                'getters': [{'id'}, {'f_integer', 'five_1_1'}, {'five_1_1'}],
            },
            ItemConstraintsSelf: {
                'creators': [{'code', 'second_parent_1_1', 'parent_x_1'}],
                'getters': [{'code'},
                            {'first_parent_1_1'}, {'first_child_1_1'},
                            {'second_parent_1_1'}, {'second_child_1_1'},],
            },
        }
        
        for item_cls in item_classes:
            #--- getters ---
            item_getters = self.__to_sorted_lists(
                item_cls.getters)
            expected_getters = self.__to_sorted_lists(
                expected[item_cls]['getters'])
            self.assertEqual(item_getters, expected_getters, item_cls)
            
            #--- creators ---
            item_creators = self.__to_sorted_lists(
                item_cls.creators)
            expected_creators = self.__to_sorted_lists(
                expected[item_cls]['creators'])
            
            self.assertEqual(item_creators, expected_creators, item_cls)
    
    
    def test_creators_getter_autoconfig_overwrite(self):
        # default overwritten
        class ItemConstraintsSelf_A(Item):
            model_cls = self.ModelConstraintsSelf
            creators = [{'parent_x_1'}]
            getters = [{'first_parent_1_1'}]
        ItemConstraintsSelf_A.complete_setup()
        
        self.assertEqual(ItemConstraintsSelf_A.creators,
                         [{'parent_x_1'}])
        self.assertEqual(ItemConstraintsSelf_A.getters,
                         [{'first_parent_1_1'}])
    

        # default not overwritten
        self.item_cls_manager.clear()
        class ItemConstraintsSelf_B(Item):
            model_cls = self.ModelConstraintsSelf
        ItemConstraintsSelf_B.complete_setup()
        
        self.assertEqual(self.__to_sorted_lists(ItemConstraintsSelf_B.creators),
                         self.__to_sorted_lists(
                             [{'code', 'second_parent_1_1', 'parent_x_1'}]))
        self.assertEqual(self.__to_sorted_lists(ItemConstraintsSelf_B.getters),
                         self.__to_sorted_lists(
                            [{'code'},
                             {'first_parent_1_1'}, {'first_child_1_1'},
                             {'second_parent_1_1'}, {'second_child_1_1'},]))
        
        # default creators merge
        self.item_cls_manager.clear()
        class ItemConstraintsSelf_C(Item):
            model_cls = self.ModelConstraintsSelf
            creators = [{'f_binary'}]
            creators_autoconfig = True
            autoinject_creators = False
            getters = [{'f_boolean'}]
            getters_autoconfig = False
        ItemConstraintsSelf_C.complete_setup()
        
        self.assertEqual(self.__to_sorted_lists(ItemConstraintsSelf_C.creators),
                         self.__to_sorted_lists(
                            [{'f_binary'},
                             {'code', 'second_parent_1_1', 'parent_x_1'}]))
        self.assertEqual(self.__to_sorted_lists(ItemConstraintsSelf_C.getters),
                         self.__to_sorted_lists([{'f_boolean'}]))
        
        # default getters merge
        self.item_cls_manager.clear()
        class ItemConstraintsSelf_D(Item):
            model_cls = self.ModelConstraintsSelf
            creators = [{'f_binary'}]
            creators_autoconfig = False
            autoinject_creators = False
            getters = [{'f_boolean'}]
            getters_autoconfig = True
        ItemConstraintsSelf_D.complete_setup()
        
        self.assertEqual(self.__to_sorted_lists(ItemConstraintsSelf_D.creators),
                         self.__to_sorted_lists([{'f_binary'}]))
        self.assertEqual(self.__to_sorted_lists(ItemConstraintsSelf_D.getters),
                         self.__to_sorted_lists(
                            [{'f_boolean'},
                             {'code'},
                             {'first_parent_1_1'}, {'first_child_1_1'},
                             {'second_parent_1_1'}, {'second_child_1_1'},]))
        
        # creators extended
        self.item_cls_manager.clear()
        class ItemConstraintsSelf_E(Item):
            model_cls = self.ModelConstraintsSelf
        ItemConstraintsSelf_E.complete_setup()
        
        self.assertEqual(self.__to_sorted_lists(ItemConstraintsSelf_E.creators),
                         self.__to_sorted_lists([{'code',
                                                  'second_parent_1_1',
                                                  'parent_x_1'}]))
        
        self.item_cls_manager.clear()
        class ItemConstraintsSelf_F(Item):
            model_cls = self.ModelConstraintsSelf
            creators = [{'f_binary'}, {'f_boolean', 'code'}]
            creators_autoconfig = False
            autoinject_creators = True  # prevented by `autoinject_creators`
        ItemConstraintsSelf_F.complete_setup()
        
        self.assertEqual(self.__to_sorted_lists(ItemConstraintsSelf_F.creators),
                         self.__to_sorted_lists([{'f_binary'},
                                                 {'f_boolean', 'code'}]))
        
        self.item_cls_manager.clear()
        class ItemConstraintsSelf_G(Item):
            model_cls = self.ModelConstraintsSelf
            creators = [{'f_binary'}, {'f_boolean', 'code'}]
            creators_autoconfig = True
            autoinject_creators = True  # creator groups must be extended
        ItemConstraintsSelf_G.complete_setup()
         
        self.assertEqual(self.__to_sorted_lists(ItemConstraintsSelf_G.creators),
                         self.__to_sorted_lists([{'f_binary',
                                                  'code',
                                                  'second_parent_1_1',
                                                  'parent_x_1'},
                                                 {'f_boolean',
                                                  'code',
                                                  'second_parent_1_1',
                                                  'parent_x_1'}]))
        
        # but do not extend if group already there
        self.item_cls_manager.clear()
        class ItemConstraintsSelf_H(Item):
            model_cls = self.ModelConstraintsSelf
            creators = [{'code',
                         'second_parent_1_1', 'parent_x_1'}]
            creators_autoconfig = True
            autoinject_creators = True
        ItemConstraintsSelf_H.complete_setup()
         
        self.assertEqual(self.__to_sorted_lists(ItemConstraintsSelf_H.creators),
                         self.__to_sorted_lists([{'code',
                                                  'second_parent_1_1',
                                                  'parent_x_1'}]))
        
    
    def test_defaults_injection(self):
        self.setup_models(self, one_conf={
                'defaults': {'f_integer': '100', 'f_boolean': 'true',
                             'f_string': lambda item: 'INT: {}'.format(
                                 item['f_integer'])}
            })
        
        item = self.ItemGeneralOne(f_integer='400')
        item.process()
        self.assertEqual(item['f_integer'], 400)
        self.assertIs(item['f_boolean'], True)
        self.assertEqual(item['f_string'], 'INT: 400')
        
        item = self.ItemGeneralOne(f_boolean='false')
        item.process()
        self.assertEqual(item['f_integer'], 100)
        self.assertIs(item['f_boolean'], False)
        self.assertEqual(item['f_string'], 'INT: 100')
        
    
    def test_default_relations_injection(self):
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
        
        # regular default values -----------------------------------------------
        ItemGeneralTwo.defaults.update({
            'one_1_1': ItemGeneralOne(f_float='11'),
            # bulk as list
            'one_1_x': [ItemGeneralOne(f_float='19.1'),
                        ItemGeneralOne(f_float='19.2')],
            'one_x_x': ItemGeneralOne.Bulk(),
        })
        ItemGeneralTwo.defaults['one_x_x'].gen(f_float='99.1')
        ItemGeneralTwo.defaults['one_x_x'].gen(f_float='99.2')
        
        item_two = ItemGeneralTwo(f_float='2')
        item_two.process()
        
        # making sure that all items were processed (converted to float)
        self.assertEqual(item_two['f_float'], 2)
        self.assertEqual(item_two['one_1_1']['f_float'], 11)
        self.assertEqual(item_two['one_1_x'][0]['f_float'], 19.1)
        self.assertEqual(item_two['one_1_x'][1]['f_float'], 19.2)
        self.assertEqual(item_two['one_x_x'][0]['f_float'], 99.1)
        self.assertEqual(item_two['one_x_x'][1]['f_float'], 99.2)
        
        # must not be overwritten with default
        item_two = ItemGeneralTwo(f_float='2.2',
                                  one_1_1=ItemGeneralOne(f_float='11.2'),
                                  one_1_x=[ItemGeneralOne(f_float='19.12'),
                                           ItemGeneralOne(f_float='19.22')])
        item_two['one_x_x'].add(ItemGeneralOne(f_float='99.12'),
                                ItemGeneralOne(f_float='99.22'))
        item_two.process()
        self.assertEqual(item_two['f_float'], 2.2)
        self.assertEqual(item_two['one_1_1']['f_float'], 11.2)
        self.assertEqual(item_two['one_1_x'][0]['f_float'], 19.12)
        self.assertEqual(item_two['one_1_x'][1]['f_float'], 19.22)
        self.assertEqual(item_two['one_x_x'][0]['f_float'], 99.12)
        self.assertEqual(item_two['one_x_x'][1]['f_float'], 99.22)
        
        # function default values ----------------------------------------------
        def gen_bulk_item(_):
            bulk_two = ItemGeneralTwo.Bulk()
            bulk_two.gen(f_float='99.1')
            bulk_two.gen(f_float='99.2')
            return bulk_two
        
        ItemGeneralOne.defaults.update({
            'two_1_1': lambda _: ItemGeneralTwo(f_float='11'),
            # bulk as list
            'two_1_x': lambda _: [ItemGeneralTwo(f_float='19.1'),
                                  ItemGeneralTwo(f_float='19.2')],
            'two_x_x': gen_bulk_item,
        })
        
        item_one = ItemGeneralOne(f_float='1')
        item_one.process()
        
        # making sure that all items were processed (converted to float)
        self.assertEqual(item_one['f_float'], 1)
        self.assertEqual(item_one['two_1_1']['f_float'], 11)
        self.assertEqual(item_one['two_1_x'][0]['f_float'], 19.1)
        self.assertEqual(item_one['two_1_x'][1]['f_float'], 19.2) 
        self.assertEqual(item_one['two_x_x'][0]['f_float'], 99.1)
        self.assertEqual(item_one['two_x_x'][1]['f_float'], 99.2)
        
        # must not be overwritten with default
        item_one = ItemGeneralOne(f_float='1.2',
                                  two_1_1=ItemGeneralTwo(f_float='11.2'),
                                  two_1_x=[ItemGeneralTwo(f_float='19.12'),
                                           ItemGeneralTwo(f_float='19.22')])
        item_one['two_x_x'].add(ItemGeneralTwo(f_float='99.12'),
                                ItemGeneralTwo(f_float='99.22'))
        item_one.process()
        self.assertEqual(item_one['f_float'], 1.2)
        self.assertEqual(item_one['two_1_1']['f_float'], 11.2)
        self.assertEqual(item_one['two_1_x'][0]['f_float'], 19.12)
        self.assertEqual(item_one['two_1_x'][1]['f_float'], 19.22)
        self.assertEqual(item_one['two_x_x'][0]['f_float'], 99.12)
        self.assertEqual(item_one['two_x_x'][1]['f_float'], 99.22)
        
        
    def test_invalid_field_name(self):
        class InvalidItem(Item):
            model_cls = self.ModelInvalidFieldNames

        with self.assertRaises(InvalidFieldName):
            InvalidItem()
    
    
    def test_aliases_process(self):
        self.setup_models(
            one_conf={
                'aliases': {
                    'alias_1': 'two_x_1__f_integer',
                    'alias_2': 'two_x_x__f_integer',
                }
            },
            two_conf={
                'aliases': {
                    'alias_1__post': 'f_float',
                    'alias_2__post': 'one_x_1__alias_1',
                    'alias_3__post': 'one_x_x__two_x_1__alias_1__post',
                }
            },
            clear_registry=True)

        # processing individual fields
        value = self.ItemGeneralOne.process_field('alias_1', '1')
        self.assertEqual(value, 1)
        
        value = self.ItemGeneralTwo.process_field('alias_1__post', '3.3')
        self.assertEqual(value, 3.3)
        value = self.ItemGeneralTwo.process_field('alias_2__post', '4')
        self.assertEqual(value, 4)
        value = self.ItemGeneralTwo.process_field('alias_3__post', '5.5')
        self.assertEqual(value, 5.5)
        
        # processing items
        item = self.ItemGeneralOne(alias_1='1',
                                   alias_2='2',
                                   two_1_1__alias_1__post='3.3',
                                   two_1_1__alias_2__post='5',
                                   two_1_1__alias_3__post='5.5')
        item.process()
        expect = {
            'id': 1,
            'item': {
                'two_1_1': {
                    'id': 2,
                    'item': {
                        'f_float': 3.3,
                        'one_1_1': {
                            'id': 1
                        },
                        'one_x_1': {
                            'id': 3,
                            'item': {
                                'two_1_x': {
                                    'bulk': [
                                        {
                                            'id': 2
                                        }
                                    ],
                                    'defaults': {}
                                },
                                'two_x_1': {
                                    'item': {
                                        'f_integer': 5,
                                        'one_1_x': {
                                            'bulk': [
                                                {
                                                    'id': 3
                                                }
                                            ],
                                            'defaults': {}
                                        }
                                    }
                                }
                            }
                        },
                        'one_x_x': {
                            'bulk': [],
                            'defaults': {
                                'two_x_1__f_float': 5.5
                            }
                        }
                    }
                },
                'two_x_1': {
                    'item': {
                        'f_integer': 1,
                        'one_1_x': {
                            'bulk': [
                                {
                                    'id': 1
                                }
                            ],
                            'defaults': {}
                        }
                    }
                },
                'two_x_x': {
                    'bulk': [],
                    'defaults': {
                        'f_integer': 2
                    }
                }
            }
        }
        self.assertEqual(item.to_dict(), expect)

        bulk = self.ItemGeneralOne.Bulk()
        # generating same item as before
        bulk.gen(alias_1='1',
                 alias_2='2',
                 two_1_1__alias_1__post='3.3',
                 two_1_1__alias_2__post='5',
                 two_1_1__alias_3__post='5.5')
        # two_x_1__one_x_x__two_x_1__f_float
        bulk['two_x_1__alias_3__post'] = '6.6'
        bulk.process()
        
        expect = {
            'bulk': [
                {
                    'id': 1,
                    'item': {
                        'two_1_1': {
                            'id': 2,
                            'item': {
                                'f_float': 3.3,
                                'one_1_1': {
                                    'id': 1
                                },
                                'one_x_1': {
                                    'id': 3,
                                    'item': {
                                        'two_1_x': {
                                            'bulk': [
                                                {
                                                    'id': 2
                                                }
                                            ],
                                            'defaults': {}
                                        },
                                        'two_x_1': {
                                            'item': {
                                                'f_integer': 5,
                                                'one_1_x': {
                                                    'bulk': [
                                                        {
                                                            'id': 3
                                                        }
                                                    ],
                                                    'defaults': {}
                                                }
                                            }
                                        }
                                    }
                                },
                                'one_x_x': {
                                    'bulk': [],
                                    'defaults': {
                                        'two_x_1__f_float': 5.5
                                    }
                                }
                            }
                        },
                        'two_x_1': {
                            'item': {
                                'f_integer': 1,
                                'one_1_x': {
                                    'bulk': [
                                        {
                                            'id': 1
                                        }
                                    ],
                                    'defaults': {}
                                },
                                'one_x_x': {
                                    'bulk': [],
                                    'defaults': {
                                        'two_x_1__f_float': 6.6
                                    }
                                }
                            }
                        },
                        'two_x_x': {
                            'bulk': [],
                            'defaults': {
                                'f_integer': 2
                            }
                        }
                    }
                }
            ],
            'defaults': {
                # two_x_1__alias_3__post
                'two_x_1__one_x_x__two_x_1__f_float': 6.6
            }
        }
        self.assertEqual(bulk.to_dict(), expect)
    
    
    def test_invalid_alias(self):
        with self.assertRaises(WrongAlias):
            self.setup_models(
                one_conf={
                    'aliases': {
                        'alias_1': 'two_1_1__f_integer',
                        'alias_2': 'two_x_x__one_1_1__f_integer__invaliad_alias',
                    }
                },
                clear_registry=True)
        
        
    def test_creators_and_getters_mix(self):
        self.item_cls_manager.autogenerate = True
        
        class ItemConstraintsOne(Item):
            model_cls = self.ModelConstraintsOne
            
            getters = ['three_1_x', 'f_integer']
            getters_autoconfig = True
            
            creators = ['three_1_x', 'f_integer']
            creators_autoconfig = True

            
        class ItemConstraintsThree(Item):
            model_cls = self.ModelConstraintsOne
        
        ItemConstraintsOne.complete_setup()
        ItemConstraintsThree.complete_setup()
        
        expected_getters = [{'three_1_x'}, {'f_integer'},
                            {'five_1_1'}, {'f_string'}, {'id'}]
        expected_creators = [{'three_1_x'}, {'f_integer'},
                             {'f_text', 'f_string'}]
        
        def sorted_groups(groups):
            subgroups = []
            for subgroup in groups:
                subgroup = list(subgroup)
                subgroup.sort()
                subgroups.append(subgroup)
            subgroups.sort()
        
        self.assertEqual(sorted_groups(ItemConstraintsOne.getters),
                         sorted_groups(expected_getters))
        self.assertEqual(sorted_groups(ItemConstraintsOne.creators),
                         sorted_groups(expected_creators))

        
    
