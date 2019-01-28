from save_to_db.adapters.utils.adapter_manager import get_adapter_cls
from save_to_db.adapters.utils.column_type import ColumnType
from save_to_db.adapters.utils.relation_type import RelationType

from save_to_db.utils.test_base import TestBase



class TestFieldsAndRelations(TestBase):
    """ Tests that adapter correctly identifies model column types and
    relationship types of foreign keys.
    """
    
    # models that are needed for tests to run
    ModelFieldTypes = None
    ModelGeneralOne = None
    ModelGeneralTwo = None
    
    
    def test_iter_fields(self):
        #--- test column types ---
        model_cls = self.ModelFieldTypes
        adapter_cls = get_adapter_cls(model_cls)
        
        required_column_types = [ct for ct in ColumnType.__members__.values()
                                    if ct != ColumnType.OTHER]

        for col_name, col_type in adapter_cls.iter_fields(model_cls):
            if col_name == 'id':
                continue  # ignoring "id" field
            if col_type in required_column_types:
                required_column_types.remove(col_type)
            
            col_type_from_name = col_name.split('_', 2)[0].upper()
            self.assertEqual(col_type_from_name, col_type.name,
                             'Wrong column type for: {}'.format(col_name))

        self.assertTrue(len(required_column_types) == 0,
                        'Not all columns types were defined, missing: {}'
                            .format(', '.join(t.name for t in
                                              required_column_types)))
        
        #--- foreign keys must not be reported ---
        model_cls = self.ModelGeneralOne
        expected_fields = {
            ('id', ColumnType.INTEGER),
            ('f_binary', ColumnType.BINARY),
            ('f_boolean', ColumnType.BOOLEAN),
            ('f_string', ColumnType.STRING),
            ('f_text', ColumnType.TEXT),
            ('f_integer', ColumnType.INTEGER),
            ('f_float', ColumnType.FLOAT),
            ('f_date', ColumnType.DATE),
            ('f_time', ColumnType.TIME),
            ('f_datetime', ColumnType.DATETIME),
        }
        
        actual_fields = set(
            (fname, ftype)
            for fname, ftype, in adapter_cls.iter_fields(model_cls))
        
        self.assertFalse(expected_fields - actual_fields,
                         'Not all columns were reported')
        self.assertFalse(actual_fields - expected_fields,
                         'Extra columns were reported')
        
    
    def test_iter_relations(self):
        model_one = self.ModelGeneralOne
        model_two = self.ModelGeneralTwo
        
        adapter_cls = get_adapter_cls(model_one)
        
        #--- model_one ---
        
        expected_relation_set = {
            # self relations
            ('parent_1_1', model_one, RelationType.ONE_TO_ONE, 'child_1_1'),
            ('child_1_1', model_one, RelationType.ONE_TO_ONE, 'parent_1_1'),
            ('parent_x_1', model_one, RelationType.MANY_TO_ONE, 'child_1_x'),
            ('child_1_x', model_one, RelationType.ONE_TO_MANY, 'parent_x_1'),
            ('parent_x_x', model_one, RelationType.MANY_TO_MANY, 'child_x_x'),
            ('child_x_x', model_one, RelationType.MANY_TO_MANY, 'parent_x_x'),
            # relations with other
            ('two_1_1', model_two, RelationType.ONE_TO_ONE, 'one_1_1'),
            ('two_1_x', model_two, RelationType.ONE_TO_MANY, 'one_x_1'),
            ('two_x_1', model_two, RelationType.MANY_TO_ONE, 'one_1_x'),
            ('two_x_x', model_two, RelationType.MANY_TO_MANY, 'one_x_x'),
        }
        actual_relation_set = set(adapter_cls.iter_relations(model_one))

        # not all relations reported?
        not_reported_relations = expected_relation_set - actual_relation_set
        self.assertFalse(
            bool(not_reported_relations),
            'Not all relations reported for {}, not reported: {}'.format(
                 model_one.__name__, str(not_reported_relations)))
        
        # reported extra relations?
        extra_relations = actual_relation_set - expected_relation_set
        self.assertFalse(extra_relations,
                         'Extra relations reported for {}'.format(
                             model_one.__name__))
        
        # relation reported twice?
        actual_relation_list = list(adapter_cls.iter_relations(model_one))
        actual_relation_list.sort()
        for actual_relation in actual_relation_set:
            actual_relation_list.remove(actual_relation)
        actual_relation_list = list(set(actual_relation_list))
        actual_relation_list.sort()
        self.assertFalse(actual_relation_list,
                         'Relations reported more then once for {}'.format(
                             model_one.__name__))
        
        
        #--- model_two ---

        expected_relation_set = {
            # self relations
            ('parent_1_1', model_two, RelationType.ONE_TO_ONE, 'child_1_1'),
            ('child_1_1', model_two, RelationType.ONE_TO_ONE, 'parent_1_1'),
            ('parent_x_1', model_two, RelationType.MANY_TO_ONE, 'child_1_x'),
            ('child_1_x', model_two, RelationType.ONE_TO_MANY, 'parent_x_1'),
            ('parent_x_x', model_two, RelationType.MANY_TO_MANY, 'child_x_x'),
            ('child_x_x', model_two, RelationType.MANY_TO_MANY, 'parent_x_x'),
            # relations with other
            ('one_1_1', model_one, RelationType.ONE_TO_ONE, 'two_1_1'),
            ('one_1_x', model_one, RelationType.ONE_TO_MANY, 'two_x_1'),
            ('one_x_1', model_one, RelationType.MANY_TO_ONE, 'two_1_x'),
            ('one_x_x', model_one, RelationType.MANY_TO_MANY, 'two_x_x'),
        }
        actual_relation_set = set(adapter_cls.iter_relations(model_two))
        
        # not all relations reported?
        not_reported_relations = expected_relation_set - actual_relation_set
        self.assertFalse(not_reported_relations,
                         'Not all relations reported for {}'.format(
                             model_two.__name__))
        
        # reported extra relations?
        extra_relations = actual_relation_set - expected_relation_set
        self.assertFalse(extra_relations,
                         'Extra relations reported for {}'.format(
                             model_two.__name__))
        
        # relation reported twice?
        actual_relation_list = list(adapter_cls.iter_relations(model_two))
        actual_relation_list.sort()
        for actual_relation in actual_relation_set:
            actual_relation_list.remove(actual_relation)
        actual_relation_list = list(set(actual_relation_list))
        actual_relation_list.sort()
        self.assertFalse(actual_relation_list,
                         'Relations reported more then once for {}'.format(
                             model_two.__name__))
    
    
    def test_table_fullname(self):
        adapter_cls = get_adapter_cls(self.ModelFieldTypes)
        
        table_name = adapter_cls.get_table_fullname(self.ModelFieldTypes)
        self.assertEqual(table_name, 'model_field_types')
        
        table_name = adapter_cls.get_table_fullname(self.ModelGeneralOne)
        self.assertEqual(table_name, 'model_general_one')
        
        table_name = adapter_cls.get_table_fullname(self.ModelGeneralTwo)
        self.assertEqual(table_name, 'model_general_two')
    
    
    
    
    
    
    