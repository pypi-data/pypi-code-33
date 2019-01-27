from save_to_db.core.item import Item
from save_to_db.utils.test_base import TestBase


class TestItemHooks(TestBase):
    """ This class contains tests that make sure that item hooks are called at
    proper times and arguments.
    """
    ModelGeneralOne = None
    ModelGeneralTwo = None
    
    def setup_models(self,
                     one_dict=None, two_dict=None,
                     one_conf=None, two_conf=None,
                     clear_registry=False):
        if clear_registry:
            self.item_cls_manager.clear()
        
        one_dict = one_dict if one_dict is not None else {}
        one_dict['model_cls'] = self.ModelGeneralOne
        if one_conf:
            one_dict.update(one_conf)
        self.ItemGeneralOne = type('ItemGeneralOne', (Item,), one_dict)

        two_dict = one_dict if two_dict is not None else {}
        two_dict['model_cls'] = self.ModelGeneralTwo
        if two_conf:
            two_dict.update(two_conf)
        self.ItemGeneralTwo = type('ItemGeneralTwo', (Item,), two_dict)
    
    
    def test_before_and_after_process(self):
        process_log = []
        def before_process(item):
            self.assertIsInstance(item['f_integer'], str)  # still a string
            process_log.append('BEFORE {}: {} ({})'.format(
                item.__class__.__name__, item['f_integer'],
                type(item['f_integer']).__name__))
        
        def after_process(item):
            self.assertIsInstance(item['f_integer'], int)  # an integer
            process_log.append('AFTER {}: {} ({})'.format(
                item.__class__.__name__, item['f_integer'],
                type(item['f_integer']).__name__))
    
        self.setup_models(one_dict={'before_process': before_process,
                                    'after_process': after_process},
                          two_dict={'before_process': before_process,
                                    'after_process': after_process})
        
        item_one = self.ItemGeneralOne(f_integer='1000')
        for i in range(2):
            item_one['two_x_x'].gen(f_integer=str(2000+i))
        
        item_one.process()
        
        expected_log =  ['BEFORE ItemGeneralOne: 1000 (str)',
                         'BEFORE ItemGeneralTwo: 2000 (str)',
                         'AFTER ItemGeneralTwo: 2000 (int)',
                         'BEFORE ItemGeneralTwo: 2001 (str)',
                         'AFTER ItemGeneralTwo: 2001 (int)',
                         'AFTER ItemGeneralOne: 1000 (int)']
        
        self.assertEqual(process_log, expected_log)
    
    
    def test_before_and_after_persist(self):
        update_log = []
        
        def before_model_update(item, model):
            update_log.append([
                'before_model_update',
                [item['f_integer'], type(item['f_integer']).__name__],
                model.f_integer,
            ])
        
        def after_model_update(item, model):
            update_log.append([
                'after_model_update',
                [item['f_integer'], type(item['f_integer']).__name__],
                model.f_integer,
            ])
        
        persister = self.persister
        
        self.setup_models(one_dict={'before_model_update': before_model_update,
                                    'after_model_update': after_model_update},
                          one_conf={'creators': ['f_float'],
                                    'getters': ['f_float']},
                          two_dict={'before_model_update': before_model_update,
                                    'after_model_update': after_model_update},
                          two_conf={'creators': ['f_float'],
                                    'getters': ['f_float']},)
        
        # initial item persisted, some items in a bulk omitted -----------------
        item_one = self.ItemGeneralOne(f_integer='1000', f_float='10.1')
        for i in range(3):
            item_two = item_one['two_x_x'].gen(f_integer=str(2000+i))
            if i % 2 == 0:  # some items will be omitted
                item_two['f_float'] = str(2100+i)
        
        persister.persist(item_one)
        
        expected = [
            ['before_model_update', [2000, 'int'], None],
            ['after_model_update', [2000, 'int'], 2000],
            # item with `f_integer='2001'` was not creatable
            ['before_model_update', [2002, 'int'], None],
            ['after_model_update', [2002, 'int'], 2002],
            ['before_model_update', [1000, 'int'], None],
            ['after_model_update', [1000, 'int'], 1000]
        ]
        
        sort_func = lambda x: (x[0], x[1][0], x[2],)
        expected.sort(key=sort_func)
        update_log.sort(key=sort_func)
        
        self.assertTrue(update_log == expected)
        
        # initial item omitted -------------------------------------------------
        update_log.clear()
        
        item_one = self.ItemGeneralOne(f_integer='10000')
        # 1 item updated, 1 item created
        for i in range(2):
            item_one['two_x_x'].gen(f_integer=str(2000+i), f_float=str(2100+i))
        
        persister.persist(item_one)
        

        expected = [
            ['before_model_update', [2000, 'int'], 2000],  # updated
            ['after_model_update', [2000, 'int'], 2000],
            ['before_model_update', [2001, 'int'], None],  # created
            ['after_model_update', [2001, 'int'], 2001],
        ]
        
        expected.sort(key=sort_func)
        update_log.sort(key=sort_func)
        
        self.assertTrue(update_log == expected)
    
    
    def test_item_hooks_order(self):
        log = []
        def before_process(*_args, **_kwargs):
            log.append('before_process')
        def after_process(*_args, **_kwargs):
            log.append('after_process')
        def before_model_update(*_args, **_kwargs):
            log.append('before_model_update')
        def after_model_update(*_args, **_kwargs):
            log.append('after_model_update')
            
        self.setup_models(one_dict={'before_process': before_process,
                                    'after_process': after_process,
                                    'before_model_update': before_model_update,
                                    'after_model_update': after_model_update})
        
        item_one = self.ItemGeneralOne(f_integer='1000')
        self.persister.persist(item_one)
        
        expected_log = ['before_process',
                    'after_process',
                    'before_model_update',
                    'after_model_update']
        self.assertTrue(log, expected_log)