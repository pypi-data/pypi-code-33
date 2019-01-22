""" Module that contains tests for adapters. The tests require next models:

    Models for basic adapter tests:

        - `ModelFieldTypes` with columns defined according to the rules:
            
            - "id" can be present or not (ignored).
            - Model fields (table columns) must be prefixed with it's type and
              underscore, for example: "integer_first". Types are just lower
              case versions of
              :py:class:`~save_to_db.adapters.utils.column_type.ColumnType`
              enumeration members.
            - Column names in database must be prefixed with 'new_'.
            - All types must be used at least once, except for `OTHER` type
              which must be not used at all.
    
    Models for basic relationship tests, must contains all types of
    relationships between different models and with self:
    
        - `ModelGeneralOne` and `ModelGeneralTwo`
          with next fields, relations and other definitions:
          
            - `ModelGeneralOne` must have "model_general_one" table name,
              `ModelGeneralTwo` must have "model_general_two" table name.
            - "id" primary key and any other fields used only as foreign keys.
            - both table must have next self referencing fields: 
                
                - "id" primary key
                - `parent_x_1` many-to-one relationship, `child_1_x` many-to-one
                  relationship on the other side.
                - `parent_1_1` one-to-one relationship, `child_1_1` one-to-one
                  relationship on the other side.
                - `parent_x_x` many-to-many relationship, `child_x_x`
                  many-to-many relationship on the other side.
                - "f_binary", "f_boolean", "f_string", "f_text", "f_integer",
                  "f_float", "f_date", "f_time", "f_datetime" columns with
                  appropriate types
            
            - `ModelGeneralOne.two_1_x` one-to-many relationship,
              `ModelGeneralTwo.one_x_1` many-to-one relationship
              on the other side.
            - `ModelGeneralOne.two_1_1` one-to-one relationship,
              `ModelGeneralTwo.one_1_1` one-to-one relationship
              on the other side.
            - `ModelGeneralOne.two_x_x` many-to-many
              relationship, `ModelGeneralTwo.one_x_x` many-to-many
              relationship on the other side.
            - `ModelGeneralOne.two_x_1` many-to-one relationship,
              `ModelGeneralTwo.one_1_x` one-to-many relationship
              on the other side.
              
            - all foreign keys must be "delete on cascade".
            
        - `ModelManyRefsOne` and `ModelManyRefsTwo`
          with next fields, relations and other definitions:
          
            - `ModelManyRefsOne` must have "model_many_refs_one" table name,
              `ModelManyRefsTwo` must have "model_many_refs_two" table name.
            - "id" primary key.
            
            - `ModelManyRefsOne.two_x_1_a` many-to-one relationship,
              `ModelManyRefsTwo.one_1_x_a` one-to-many relationship
              on the other side.
            - `ModelManyRefsOne.two_1_x_b` one-to-many relationship,
              `ModelManyRefsTwo.one_x_1_b` many-to-many relationship
              on the other side.
              
            - `ModelManyRefsOne.two_x_x_a` many-to-many relationship,
              `ModelManyRefsTwo.one_x_x_a` many-to-many relationship
              on the other side.
            - `ModelManyRefsOne.two_x_x_b` many-to-many relationship,
              `ModelManyRefsTwo.one_x_x_b` many-to-many relationship
              on the other side.
              
            - `ModelManyRefsOne.two_1_1_a` one-to-one relationship,
              `ModelManyRefsTwo.one_1_1_a` one-to-one relationship
              on the other side. Table one has foreign key to table two.
            - `ModelManyRefsOne.two_1_1_b` one-to-one relationship,
              `ModelManyRefsTwo.one_1_1_b` one-to-one relationship
              on the other side. Table two has foreign key to table one.
              
            - all foreign keys must be "delete on cascade".
    
    Models for creators and getters auto configuration should contain:
    
        - Models with single primary key and relationships using it:
        
            - many-to-one with required value.
            - many-to-one with not required value.
            
        - Models with composite primary key:
        
            - many-to-one with required value.
            - many-to-one with not required value.
            
        - Models null constraint:
            
            - Model with not null field.
        
        - Models with unique constraints:
            
            - Model with simple unique field.
            - Model with simple unique field that cannot be null.
            - Model with composite unique constraint.
            - Model with simple foreign key that has a unique constraint.
            - Model with simple not null foreign key that has a unique
              constraint.
            - Model with simple foreign key that has a unique constraint
              together with other column.
            - Model with composite foreign key that has a unique constraint.
        
        - Model with many-to-many-relationships.
        - Model with many-to-one not null relation with itself, one-to-one
          relationship with unique constraint with itself, one-to-one not null
          relationship with unique constraint with itself, many-to-many
          relationship with itself.
        - All models must have "f_binary", "f_boolean", "f_string", "f_text",
          "f_integer", "f_float", "f_date", "f_time", "f_datetime" columns with
          appropriate types.
        
    And the models are:
    
        - `ModelConstraintsOne`:
            
            - `model_constraints_one` table name
            - `id` primary key
            - `f_text` cannot be null
            - `f_integer` unique
            - `f_string` not null and unique
            
        - `ModelConstraintsTwo`:
        
            - `model_constraints_two` table name
            - `id` primary key
            - `one_x_1_id` foreign key to `ModelConstraintsOne` with `one_x_1`
              relation and `two_1_x` on the other side
            - `three_x_x` relation with `ModelConstraintsThree` with `two_x_x`
              on the other side
            - `four_primary_one` and `four_primary_two` both not null foreign
              keys to `ModelConstraintsFour` with `four_x_1` relation and
              `two_1_x` on the other side
        
        - `ModelConstraintsThree`:
        
            - `model_constraints_three` table name
            - `id` primary key
            - `one_x_1_id` not null foreign key to `ModelConstraintsOne` with
              `one_x_1` relation and `three_1_x` on the other side
            - `two_x_x` relation with `ModelConstraintsTwo` and `three_x_x` on
              the other side
            - `four_primary_one` and `four_primary_two` foreign keys to
              `ModelConstraintsFour` that can be null, `four_x_1` relation with
              `three_1_x` on the other side
        
        - `ModelConstraintsFour`:
        
            - `model_constraints_four` table name
            - composite `primary_one` plus `primary_two` columns primary key
            - `f_integer` plus `f_string` unique constraint
            
        - `ModelConstraintsFive`:
        
            - `model_constraints_five` table name
            - `id` primary key
            - `one_1_1_id` unique foreign key to `ModelConstraintsOne` with
              `one_1_1` relation and `five_1_1` on the other side
            - `four_primary_one` plus `four_primary_two` unique foreign key
              to `ModelConstraintsFour` with `four_1_1` relation and `five_1_1`
              on the other side
        
        - `ModelConstraintsSix`:
        
            - `model_constraints_six` table name
            - `id` primary key
            - `five_1_1_id` not null foreign key to `ModelConstraintsFive` with
              `five_1_1` relation and `six_1_1` on the other side
            - `five_1_1_id` plus `f_integer` unique constraint
            
        - `ModelConstraintsSelf`:
        
            - `model_constraints_self` table name
            - `id` primary key
            - `parent_x_1_id` not null foreign key to itself with `parent_x_1`
              relation and `child_1_x` on the other side.
            - `first_parent_1_1_id` foreign key with unique constraint to
              itself with `first_parent_1_1` relation and `first_child_1_1` on
              the other side.
            - `parent_x_x` many-to-many relationship with itself with
              `child_x_x` on the other side.
    
    Model for testing default model values:
    
        - `ModelDefaultValues`:
        
            - `model_default_values` table name.
            - `id` primary key.
            - `f_integer` with no default value, not null.
            - `f_boolean` with `True` default value, not null.
            - `f_string` with 'default_string' default value, not null.
            - `f_text` with default value defined by a function, not null.
            
    Models for testing reverse relations:
    
        Models here must include all possible kinds of setting up relationships,
        manual and automatic.
        - All tables must have "f_binary", "f_boolean", "f_string", "f_text",
          "f_integer", "f_float", "f_date", "f_time", "f_datetime" columns with
          appropriate types
        - `ModelAutoReverseOne`:
            - `model_auto_reverse_one` table name
            - `two_b_1_1_id` foreign key to `ModelAutoReverseTwoB` with
              `two_b_1_1` with no relation on the other side.
            - `three_b_x_1_id` foreign key to `ModelAutoReverseTwoB` with
              `three_b_x_1` with no relation on the other side.
            - `four_b_x_x` to `ModelAutoReverseFourB` with no relation on the
               other side.
            - any other relations.
            - `f_string`
        - `ModelAutoReverseTwoA`:
            - `model_auto_reverse_two_a` table name
            - any relations.
        - `ModelAutoReverseTwoB`:
            - `model_auto_reverse_two_b` table name
            - any relations.
        - `ModelAutoReverseThreeA`:
            - `model_auto_reverse_three_a` table name
            - any relations.
        - `ModelAutoReverseThreeB`:
            - `model_auto_reverse_three_b` table name
            - any relations.
        - `ModelAutoReverseFourA`:
            - `model_auto_reverse_four_a` table name
            - any relations.
        - `ModelAutoReverseFourB`:
            - `model_auto_reverse_four_b` table name
            - any relations.
        
        All models must have `ITEM_RELATIONS` constant that contains info about
        relations like this:
        
            ITEM_RELATIONS = {
                key_1: (reverse_key_1, forword_relation_type_1,),
                ...
            }
"""

import importlib
from unittest import TestCase


# tuple of database adapter names to test
ADAPTER_NAMES = (
    'sqlalchemy_adapter',
    'django_adapter',
)


def init():
    """ Loads tests for all adapters. (Loading `tests` module from
    an adapter test module must trigger registration of tests)
    """
    for adapter_name in ADAPTER_NAMES:
        module_name = \
            'save_to_db.tests.test_adapters.test_{}.register_tests'.format(
                adapter_name)
        importlib.import_module(module_name)
        

registered_tests = []

def register_test(adapter_prefix, test_base, test_case, models,
                  persister):
    """ Registers a test case to be run on test command.
    
    :param adapter_prefix: A string prefix that will be used as part of the
        test class name.
    :param test_base: Test base class to be added as one of the base classes of
        a new test case. Must contain code to create and drop tables
        from database.
    :param test_case: The test case with tests.
    :param models: A dictionary of models that are needed for tests to run.
    :param persister: An instance of
        :py:class:`~save_to_db.core.persistor.Persistor` (`autocommit`
        must be `True`).
    """
    global registered_tests
    
    new_test_case_dict = {
        'persister': persister,
        'adapter_prefix': adapter_prefix,
    }
    new_test_case_dict.update(models)
    new_test_case = type('{}{}'.format(adapter_prefix, test_case.__name__),
                         (test_base, test_case),
                         new_test_case_dict)
    registered_tests.append(new_test_case)
