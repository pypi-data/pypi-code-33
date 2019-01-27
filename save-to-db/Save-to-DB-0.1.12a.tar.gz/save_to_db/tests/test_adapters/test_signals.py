from save_to_db.core import signals

from save_to_db.core.item import Item
from save_to_db.utils.test_base import TestBase



class TestSignals(TestBase):
    
    ModelGeneralOne = None
    ModelGeneralTwo = None
    
    def test_signals_emit(self):
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'f_integer'}]
            getters = [{'f_integer'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            creators = [{'f_integer'}]
            getters = [{'f_integer'}]
        
        persister = self.persister
        
        signal_calls = {
            'before_one': 0,
            'before_two': 0,
            'after_one': 0,
            'after_two': 0,
        }
        
        item_one = ItemGeneralOne(f_integer=1)
        item_one['two_x_x'](f_integer=1)
        persister.persist(item_one)
        self.assertEqual(signal_calls, {'before_one': 0,
                                        'before_two': 0,
                                        'after_one': 0,
                                        'after_two': 0,
                                        })
        
        @signals.before_db_persist.register
        def before_db_persist_signal_one(item, item_structure):
            nonlocal expected_item, expected_item_structure
            self.assertIs(item, expected_item)
            self.assertEqual(item_structure, expected_item_structure)
            self.assertIsInstance(item_structure, dict)
            signal_calls['before_one'] += 1
        
        expected_item = item_one
        expected_item_structure = item_one.process()
        persister.persist(item_one)
        self.assertEqual(signal_calls, {'before_one': 1,
                                        'before_two': 0,
                                        'after_one': 0,
                                        'after_two': 0,
                                        })
        
        def before_db_persist_signal_two(item, item_structure):
            nonlocal expected_item, expected_item_structure
            self.assertIs(item, expected_item)
            self.assertEqual(item_structure, expected_item_structure)
            self.assertIsInstance(item_structure, dict)
            signal_calls['before_two'] += 1
        signals.before_db_persist.register(before_db_persist_signal_two)
        
        persister.persist(item_one)
        self.assertEqual(signal_calls, {'before_one': 2,
                                        'before_two': 1,
                                        'after_one': 0,
                                        'after_two': 0,
                                        })
        
        @signals.after_db_persist.register
        def after_db_persist_signal_one(top_item, items, models):
            nonlocal expected_item, signal_items, signal_models
            self.assertIs(top_item, expected_item)
            signal_items, signal_models = items, models
            signal_calls['after_one'] += 1
        
        signal_items, signal_models = None, None
        returned_items, returned_models = persister.persist(item_one)
        self.assertIs(returned_items, signal_items)
        self.assertIs(returned_models, signal_models)
        self.assertEqual(signal_calls, {'before_one': 3,
                                        'before_two': 2,
                                        'after_one': 1,
                                        'after_two': 0,
                                        })
        
        def after_db_persist_signal_two(top_item, items, models):
            nonlocal expected_item, signal_items, signal_models
            self.assertIs(top_item, expected_item)
            signal_items, signal_models = items, models
            signal_calls['after_two'] += 1
        signals.after_db_persist.register(after_db_persist_signal_two)
            
        returned_items, returned_models = persister.persist(item_one)
        self.assertIs(returned_items, signal_items)
        self.assertIs(returned_models, signal_models)
        self.assertEqual(signal_calls, {'before_one': 4,
                                        'before_two': 3,
                                        'after_one': 2,
                                        'after_two': 1,
                                        })
        
        # unregister
        signals.before_db_persist.unregister(before_db_persist_signal_one)
        signals.after_db_persist.unregister(after_db_persist_signal_one)
        
        returned_items, returned_models = persister.persist(item_one)
        self.assertIs(returned_items, signal_items)
        self.assertIs(returned_models, signal_models)
        self.assertEqual(signal_calls, {'before_one': 4,
                                        'before_two': 4,
                                        'after_one': 2,
                                        'after_two': 2,
                                        })
            