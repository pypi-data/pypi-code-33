from save_to_db.adapters.utils.adapter_manager import get_adapter_cls

from save_to_db.utils.test_base import TestBase



class TestConstraints(TestBase):
    """ Tests that an adapter correctly returns not null and unique fields. """
    
    ModelConstraintsOne = None
    ModelConstraintsTwo = None
    ModelConstraintsThree = None
    ModelConstraintsFour = None
    ModelConstraintsFive = None
    ModelConstraintsSix = None
    ModelConstraintsSelf = None

        
    def test_iter_required_fields(self):
        adapter_cls = get_adapter_cls(self.ModelConstraintsOne)
        composites = adapter_cls.COMPOSITE_KEYS_SUPPORTED
        
        expected_not_nulls = [
            [self.ModelConstraintsOne, {'f_string', 'f_text'}],
            [self.ModelConstraintsTwo, {'four_x_1'}],
            [self.ModelConstraintsThree, {'one_x_1'}],
            [self.ModelConstraintsFour,
                {'primary_one', 'primary_two'} if composites else set()],
            [self.ModelConstraintsFive, set()],
            [self.ModelConstraintsSix, {'five_1_1'}],
            [self.ModelConstraintsSelf, {'code',
                                         'parent_x_1', 'second_parent_1_1'}],
        ]
        
        for model_cls, expected_not_null_fields in expected_not_nulls:
            not_null_fields = set(adapter_cls.iter_required_fields(model_cls))
            self.assertEqual(not_null_fields, expected_not_null_fields,
                             model_cls)
    
    
    def __to_sorted_lists(self, iterable_of_iterables):
        result = []
        for iterable in iterable_of_iterables:
            element = list(iterable)
            element.sort()
            result.append(element)
        result.sort()
        return result
    
    
    def test_iter_unique_field_combinations(self):
        adapter_cls = get_adapter_cls(self.ModelConstraintsOne)
        composites = adapter_cls.COMPOSITE_KEYS_SUPPORTED
        
        expected_uniques = [
            [self.ModelConstraintsOne, [{'id'}, {'f_integer'}, {'f_string'},
                                        ['five_1_1']]],
            [self.ModelConstraintsTwo, [{'id'}]],
            [self.ModelConstraintsThree, [{'id'}]],
            [self.ModelConstraintsFour,
                [{'primary_one', 'primary_two'} if composites else {'id'},
                 {'f_integer', 'f_string'}, {'five_1_1'}]],
            [self.ModelConstraintsFive, [{'id'}, {'one_1_1'}, {'four_1_1'},
                                         {'six_1_1'}]],
            [self.ModelConstraintsSix, [{'id'}, {'f_integer', 'five_1_1'},
                                        {'five_1_1'}]],
            [self.ModelConstraintsSelf, [{'code'},
                                         {'first_parent_1_1'},
                                         {'first_child_1_1'},
                                         {'second_parent_1_1'},
                                         {'second_child_1_1'}]],
        ]
        for model_cls, expected in expected_uniques:
            actual = self.__to_sorted_lists(
                        list(adapter_cls.iter_unique_field_combinations(
                            model_cls))
                    )
            expected = self.__to_sorted_lists(expected)
            
            self.assertEqual(actual, expected, model_cls)
       
       
            