from save_to_db.core import signals

from save_to_db.core.item import Item
from save_to_db.utils.test_base import TestBase



class TestSignals(TestBase):
    
    ModelGeneralOne = None
    ModelGeneralTwo = None
    
    def test_db_persist_signals(self):
        
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
            
    def test_item_dropped_signal(self):
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'f_integer'}]
            getters = [{'f_integer'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            creators = [{'f_integer'}]
            getters = [{'f_integer'}]
        
        persister = self.persister
        
        # dropped because cannot be created
        item_one = ItemGeneralOne(f_integer='10')
        item_two_dropped = item_one['two_x_x'].gen(f_string='str-20')
        item_one_dropped = item_two_dropped['one_x_1'](f_integer='30')
        item_one_dropped.update_only_mode = True
        
        items_to_reasons = [
            [
                item_two_dropped,
                signals.item_dropped.reason_cannot_create_not_enough_data,
            ],
            [
                item_one_dropped,
                signals.item_dropped.reason_cannot_create_update_only_mode,
            ],
        ]
        
        @signals.item_dropped.register
        def item_dropped_listener(item, reason):
            nonlocal items_to_reasons
            
            for entry in items_to_reasons:
                if entry[0] is item:
                    self.assertEqual(entry[1], reason, item)
                    items_to_reasons.remove(entry)
                    break
            else:
                raise Exception('Entry not found: [{}, {}]'.format(
                    item, reason))
            
        
        items, model_list = persister.persist(item_one)
        self.assertEqual(len(items), 1)
        self.assertEqual(len(model_list), 1)
        self.assertEqual(len(model_list[0]), 1)
        self.assertIs(items[0], item_one)
        
        self.assertEqual(len(items_to_reasons), 0)
        
        item_ones = self.get_all_models(self.ModelGeneralOne)
        self.assertEqual(len(item_ones), 1)
        item_twos = self.get_all_models(self.ModelGeneralTwo)
        self.assertEqual(len(item_twos), 0)

            
            
            
            
            
        