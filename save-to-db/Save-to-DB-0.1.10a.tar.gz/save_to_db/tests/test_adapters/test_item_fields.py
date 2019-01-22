import datetime

from save_to_db.core.exceptions import BulkItemOnetoXDefaultError, WrongAlias
from save_to_db.core.item import Item
from save_to_db.utils.test_base import TestBase



class TestItemFields(TestBase):
    """ Contains tests for setting field values and processing them for both
    normal items and bulk items. This class does not contain tests for
    persisting items to a database.
    """
    
    ModelFieldTypes = None
    ModelGeneralOne = None
    ModelGeneralTwo = None
    ModelAutoReverseOne = None
    ModelAutoReverseTwoA = None
    ModelAutoReverseTwoB = None
    ModelAutoReverseThreeA = None
    ModelAutoReverseThreeB = None
    ModelAutoReverseFourA = None
    ModelAutoReverseFourB = None
    
    
    @classmethod
    def setup_models(cls, aliased=False):
        cls.item_cls_manager.clear()
        
        class ItemFieldTypes(Item):
            model_cls = cls.ModelFieldTypes
            conversions = {
                'decimal_separator': ',',
            }
        cls.ItemFieldTypes = ItemFieldTypes
        
        dct_1 = {'model_cls': cls.ModelGeneralOne}
        dct_2 = {'model_cls': cls.ModelGeneralTwo}
        
        if aliased:
            dct_1.update({
                'aliases': {
                    'alias_1': 'two_1_1__f_integer',
                    'alias_2': 'two_x_x__one_1_1__f_integer',
                }
            })
            dct_2.update({
                'aliases': {
                    'alias_1__post': 'f_string',
                    'alias_2__post': 'one_x_1__alias_1',
                    'alias_3__post': 'one_x_x__two_1_x__alias_1__post',
                }
            })
        
        cls.ItemGeneralOne = type('ItemGeneralOne', (Item,), dct_1)
        cls.ItemGeneralTwo = type('ItemGeneralTwo', (Item,), dct_2)
        
        cls.ItemGeneralOne.complete_setup()
        cls.ItemGeneralTwo.complete_setup()
        
        
    def test_setting_fields(self):
        self.setup_models()
        
        #--- setting with correct keys ---
        item = self.ItemGeneralOne()
        item['f_integer'] = '10'
        item['two_1_1__f_string'] = 'one'
        item['two_1_1__one_1_x__f_string'] = 'two'
        item['two_1_1__one_x_x__two_x_1__f_string'] = 'three'
        bulk = item['two_1_1__one_x_x']
        bulk['f_integer'] = '20'
        bulk.gen(f_text='four')
        in_bulk_item = bulk.gen(f_text='five')
        # setting field by calling
        in_bulk_item(f_string='ITEM_CALL') 
        bulk(two_x_1__f_text='BULK_CALL')
        
        expected_value = {
            'item': {
                'f_integer': '10',
                'two_1_1': {
                    'item': {
                        'f_string': 'one',
                        'one_1_x': {
                            'bulk': [],
                            'defaults': {
                                'f_string': 'two'
                            }
                        },
                        'one_x_x': {
                            'bulk': [
                                {
                                    'item': {
                                        'f_text': 'four'
                                    }
                                },
                                {
                                    'item': {
                                        'f_string': 'ITEM_CALL',
                                        'f_text': 'five'
                                    }
                                }
                            ],
                            'defaults': {
                                'f_integer': '20',
                                'two_x_1__f_string': 'three',
                                'two_x_1__f_text': 'BULK_CALL'
                            }
                        }
                    }
                }
            }
        }
        self.assertEqual(item.to_dict(), expected_value)
        
        #--- setting with incorrect keys ---
        item = self.ItemGeneralOne()
        with self.assertRaises(WrongAlias):
            item['wrong_key'] = 'value'
        
        bulk = self.ItemGeneralOne.Bulk()
        with self.assertRaises(WrongAlias):
            bulk['wrong_key'] = 'value'
            
        #--- setting one-to-x default value in bulk
        with self.assertRaises(BulkItemOnetoXDefaultError):
            bulk['two_1_1__f_integer'] = '10'
        
        with self.assertRaises(BulkItemOnetoXDefaultError):
            bulk['two_1_x__f_integer'] = '10'
        
        # direct
        with self.assertRaises(BulkItemOnetoXDefaultError):
            bulk['two_1_1'] = self.ItemGeneralTwo()
        
        with self.assertRaises(BulkItemOnetoXDefaultError):
            bulk['two_1_x'] = self.ItemGeneralTwo()
        
        #--- aliases -----------------------------------------------------------
        self.setup_models(aliased=True)
        
        item = self.ItemGeneralOne()
        item['alias_1'] = '1'
        item['alias_2'] = '2'
        item['two_1_1__alias_1__post'] = 'str-1'
        item['two_1_1__alias_2__post'] = '3'
        item['two_1_1__alias_3__post'] = '4'
        bulk = item['two_1_x']
        bulk['alias_1__post'] = 'str-2'
        
        expected_value = {
            'item': {
                'two_1_1': {
                    'item': {
                        'f_integer': '1',  # alias_1
                        'f_string': 'str-1',  # two_1_1__alias_1__post
                        'one_x_1': {
                            'item': {
                                'two_1_1': {
                                    'item': {
                                        # two_1_1__alias_2__post
                                        'f_integer': '3'
                                    }
                                }
                            }
                        },
                        'one_x_x': {
                            'bulk': [],
                            'defaults': {
                                'two_1_x__f_string': '4'
                            }
                        }
                    }
                },
                'two_1_x': {
                    'bulk': [],
                    'defaults': {
                        'f_string': 'str-2'
                    }
                },
                'two_x_x': {
                    'bulk': [],
                    'defaults': {
                        'one_1_1__f_integer': '2'  # alias_1
                    }
                }
            }
        }
        self.assertEqual(item.to_dict(), expected_value)
        
    
    def test_getting_fields(self):
        self.setup_models()
        
        item = self.ItemGeneralOne()
        related_item = item['two_x_1__one_1_1__two_1_1'](f_integer='20',
                                                         f_string='value')
        self.assertIsInstance(related_item, self.ItemGeneralTwo)
        
        expected_value = {
            'item': {
                'two_x_1': {
                    'item': {
                        'one_1_1': {
                            'item': {
                                'two_1_1': {
                                    'item': {
                                        'f_integer': '20',
                                        'f_string': 'value',
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        self.assertEqual(item.to_dict(), expected_value)
        
        #--- aliases -----------------------------------------------------------
        self.setup_models(aliased=True)
        
        item = self.ItemGeneralOne()
        item['alias_1'] = '1'
        item['alias_2'] = '2'
        item['two_1_1__alias_1__post'] = 'str-1'
        item['two_1_1__alias_2__post'] = '3'
        item['two_1_1__alias_3__post'] = '4'
        bulk = item['two_1_x']
        bulk['alias_1__post'] = 'str-2'
        
        self.assertEqual(item['alias_1'], '1')
        self.assertEqual(item['alias_2'], '2')
        self.assertEqual(item['two_1_1__alias_1__post'], 'str-1')
        self.assertEqual(item['two_1_1__alias_2__post'], '3')
        self.assertEqual(item['two_1_1__alias_3__post'], '4')
        self.assertEqual(bulk['alias_1__post'], 'str-2')
        
    
    def test_del_from_item(self):
        self.setup_models()
        
        item = self.ItemGeneralOne()
        item['f_integer'] = '10'
        item['f_string'] = 'str-10'
        item['two_1_1__f_integer'] = '20'
        item['two_1_1__f_string'] = 'str-20'
        item['two_x_x__one_1_1__f_integer'] = '30'
        item['two_x_x__one_1_1__f_string'] = 'str-30'
        bulk = item['two_1_x']
        bulk['f_string'] = 'str-2'
        
        expect = {
            'item': {
                'f_integer': '10',
                'f_string': 'str-10',
                'two_1_1': {
                    'item': {
                        'f_integer': '20',
                        'f_string': 'str-20'
                    }
                },
                'two_1_x': {
                    'bulk': [],
                    'defaults': {
                        'f_string': 'str-2'
                    }
                },
                'two_x_x': {
                    'bulk': [],
                    'defaults': {
                        'one_1_1__f_integer': '30',
                        'one_1_1__f_string': 'str-30'
                    }
                }
            }
        }
        self.assertEqual(item.to_dict(), expect)
        
        del expect['item']['f_string']
        del item['f_string']
        self.assertEqual(item.to_dict(), expect)
        
        del expect['item']['two_1_1']['item']['f_string']
        del item['two_1_1__f_string']
        self.assertEqual(item.to_dict(), expect)
        
        del expect['item']['two_x_x']['defaults']['one_1_1__f_string']
        del item['two_x_x__one_1_1__f_string']
        self.assertEqual(item.to_dict(), expect)
        
        del bulk['f_string']
        del expect['item']['two_1_x']['defaults']['f_string']
        self.assertEqual(item.to_dict(), expect)
        
        #--- aliases -----------------------------------------------------------
        self.setup_models(aliased=True)
        
        item = self.ItemGeneralOne()
        item['alias_1'] = '1'
        item['alias_2'] = '2'
        item['two_1_1__alias_1__post'] = 'str-1'
        item['two_1_1__alias_2__post'] = '3'
        item['two_1_1__alias_3__post'] = '4'
        bulk = item['two_1_x']
        bulk['alias_1__post'] = 'str-2'
        
        expected_value = {
            'item': {
                'two_1_1': {
                    'item': {
                        'f_integer': '1',
                        'f_string': 'str-1',
                        'one_x_1': {
                            'item': {
                                'two_1_1': {
                                    'item': {
                                        'f_integer': '3'
                                    }
                                }
                            }
                        },
                        'one_x_x': {
                            'bulk': [],
                            'defaults': {
                                'two_1_x__f_string': '4'
                            }
                        }
                    }
                },
                'two_1_x': {
                    'bulk': [],
                    'defaults': {
                        'f_string': 'str-2'
                    }
                },
                'two_x_x': {
                    'bulk': [],
                    'defaults': {
                        'one_1_1__f_integer': '2'
                    }
                }
            }
        }
        self.assertEqual(item.to_dict(), expected_value)
        
        del item['alias_1']
        del expected_value['item']['two_1_1']['item']['f_integer']
        self.assertEqual(item.to_dict(), expected_value)
        
        del item['alias_2']
        del expected_value['item']['two_x_x']['defaults']['one_1_1__f_integer']
        self.assertEqual(item.to_dict(), expected_value)
        
        del item['two_1_1__alias_1__post']
        del expected_value['item']['two_1_1']['item']['f_string']
        self.assertEqual(item.to_dict(), expected_value)
        
        del item['two_1_1__alias_2__post']
        del expected_value['item']['two_1_1']['item']['one_x_1']['item']['two_1_1']['item']['f_integer']
        self.assertEqual(item.to_dict(), expected_value)
        
        del item['two_1_1__alias_3__post']
        del expected_value['item']['two_1_1']['item']['one_x_x']['defaults']['two_1_x__f_string']
        self.assertEqual(item.to_dict(), expected_value)
        
        del bulk['alias_1__post']
        del expected_value['item']['two_1_x']['defaults']['f_string']
        self.assertEqual(item.to_dict(), expected_value)
        
        
    def test_field_convesions(self):
        self.setup_models()
        
        #--- simple conversion ---
        item = self.ItemFieldTypes(
            binary_1 = 'binary data',
            string_1 = 1000,
            text_1 = 2000,
            integer_1 = '10',
            boolean_1 = 'TRUE',
            float_1 = '1.120,30',  # with comma as decimal separator and a dot
            date_1 = '2000-10-30',
            time_1 = '20:30:40',
            datetime_1 = '2000-10-30 20:30:40')
        
        item.process()
        expected_value = {
            'item': {
                'binary_1': b'binary data',
                'boolean_1': True,
                'date_1': datetime.date(2000, 10, 30),
                'datetime_1': datetime.datetime(2000, 10, 30, 20, 30, 40),
                'float_1': 1120.3,
                'integer_1': 10,
                'string_1': '1000',
                'text_1': '2000',
                'time_1': datetime.time(20, 30, 40)
            }
        }
        self.assertEqual(item.to_dict(), expected_value)
        
        item.process()  # second processing does nothing
        self.assertEqual(item.to_dict(), expected_value)
        
        #--- conversions with relations ---
        item = self.ItemGeneralOne(f_integer='10',
                                   two_x_1__f_integer='20',
                                   two_x_x__f_integer='30')
        item['two_x_x'].gen(f_integer='40')
        item.process()
        
        expected_value = {
            'id': 1,
            'item': {
                'f_integer': 10,
                'two_x_1': {
                    'item': {
                        'f_integer': 20,
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
                    'bulk': [
                        {
                            'item': {
                                'f_integer': 40,
                                'one_x_x': {
                                    'bulk': [
                                        {
                                            'id': 1
                                        }
                                    ],
                                    'defaults': {}
                                }
                            }
                        }
                    ],
                    'defaults': {
                        'f_integer': 30
                    }
                }
            }
        }
        self.assertEqual(item.to_dict(), expected_value)
        
    
    def test_inject_nullables(self):
        self.setup_models()
        
        self.item_cls_manager.clear()
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            # using normal fields
            nullables = ['f_integer', 'f_string']
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            # using relations
            nullables = ['one_1_1', 'one_x_1', 'one_1_x', 'one_x_x']
        
        # no overwrite for normal fields
        item = ItemGeneralOne(f_integer='10', f_string='20', f_text='30')
        item.process()
        expect = {
            'item': {
                'f_integer': 10,
                'f_string': '20', 
                'f_text': '30',
            }
        }
        self.assertEqual(item.to_dict(), expect)
        
        # normal fields nullables added
        item = ItemGeneralOne()
        item.process()
        expect = {
            'item': {
                'f_integer': None,
                'f_string': None,
            }
        }
        self.assertEqual(item.to_dict(), expect)
        
        # no overwrite for relations
        item = ItemGeneralTwo(one_1_1__f_integer='10',
                              one_1_1__f_string='20',
                              one_x_1__f_integer='10',
                              one_x_1__f_string='20')
        item['one_1_x'].gen(f_integer='10', f_string='20')
        item['one_x_x'].gen(f_integer='10', f_string='20')
        item.process()
        expect = {
            'id': 1,
            'item': {
                'one_1_1': {
                    'item': {
                        'f_integer': 10,
                        'f_string': '20',
                        'two_1_1': {
                            'id': 1
                        }
                    }
                },
                'one_1_x': {
                    'bulk': [
                        {
                            'item': {
                                'f_integer': 10,
                                'f_string': '20',
                                'two_x_1': {
                                    'id': 1
                                }
                            }
                        }
                    ],
                    'defaults': {}
                },
                'one_x_1': {
                    'item': {
                        'f_integer': 10,
                        'f_string': '20',
                        'two_1_x': {
                            'bulk': [
                                {
                                    'id': 1
                                }
                            ],
                            'defaults': {}
                        }
                    }
                },
                'one_x_x': {
                    'bulk': [
                        {
                            'item': {
                                'f_integer': 10,
                                'f_string': '20',
                                'two_x_x': {
                                    'bulk': [
                                        {
                                            'id': 1
                                        }
                                    ],
                                    'defaults': {}
                                }
                            }
                        }
                    ],
                    'defaults': {}
                }
            }
        }
        self.assertEqual(item.to_dict(), expect)
        
        # relation fields nullables added
        item = ItemGeneralTwo()
        item.process()
        expect = {
            'item': {
                'one_1_1': None,
                'one_1_x': {
                    'bulk': [],
                    'defaults': {}
                },
                'one_x_1': None,
                'one_x_x': {
                    'bulk': [],
                    'defaults': {}
                }
            }
        }
        self.assertEqual(item.to_dict(), expect)
        
    
    def test_inject_bulk_defaults(self):
        self.setup_models()
        
        self.item_cls_manager.clear()
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            # using normal fields
            nullables = ['f_integer', 'f_string']
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            # using relations
            nullables = ['one_x_1', 'one_x_x']
        
        # default regular fields
        # (first default fields must be injected only then nullables)
        bulk = ItemGeneralOne.Bulk(f_integer='1000', f_text='text-value')
        bulk.gen(f_integer='10', f_float='20.30')
        bulk.gen(f_string='str-value', f_float='20.30')
        bulk.process()
        expect = {
            'bulk': [
                {
                    'item': {
                        'f_float': 20.3,
                        'f_integer': 10,
                        'f_string': None,
                        'f_text': 'text-value'
                    }
                },
                {
                    'item': {
                        'f_float': 20.3,
                        'f_integer': 1000,
                        'f_string': 'str-value',
                        'f_text': 'text-value'
                    }
                }
            ],
            'defaults': {
                'f_integer': 1000,
                'f_text': 'text-value'
            }
        }
        self.assertEqual(bulk.to_dict(), expect)
        
        # default relations
        default_two_x_1 = ItemGeneralTwo(f_integer='10', f_float='20.30')
        default_two_x_x = ItemGeneralTwo.Bulk()
        default_two_x_x.gen(f_integer='20')
        default_two_x_x.gen(f_float='40.50')
        
        bulk = ItemGeneralOne.Bulk(two_x_1=default_two_x_1,
                                   two_x_x=default_two_x_x)
        bulk.gen(two_x_1__f_integer=40)
        bulk.gen(two_x_x__f_text='text-value')
        
        bulk.process()

        expect = {
            'bulk': [
                # first item: `bulk.gen(two_x_1__f_integer=40)`
                # + nullables + defaults
                {
                    'id': 1,
                    'item': {
                        'f_integer': None,
                        'f_string': None,
                        'two_x_1': {
                            'item': {
                                'f_integer': 40,
                                'one_1_x': {
                                    'bulk': [
                                        {
                                            'id': 1
                                        }
                                    ],
                                    'defaults': {}
                                },
                                'one_x_1': None,
                                'one_x_x': {
                                    'bulk': [],
                                    'defaults': {}
                                }
                            }
                        },
                        # `default_two_x_x = ItemGeneralTwo.Bulk()` with two
                        # items:
                        # `default_two_x_x.gen(f_integer='20')` and
                        # `default_two_x_x.gen(f_float='40.50')` + nullables
                        'two_x_x': {
                            'bulk': [
                                {
                                    'item': {
                                        'f_integer': 20,
                                        'one_x_1': None,
                                        'one_x_x': {
                                            'bulk': [
                                                {
                                                    'id': 1
                                                }
                                            ],
                                            'defaults': {}
                                        }
                                    }
                                },
                                {
                                    'item': {
                                        'f_float': 40.5,
                                        'one_x_1': None,
                                        'one_x_x': {
                                            'bulk': [
                                                {
                                                    'id': 1
                                                }
                                            ],
                                            'defaults': {}
                                        }
                                    }
                                }
                            ],
                            'defaults': {}
                        }
                    }
                },
                {
                    'id': 2,
                    'item': {
                        'f_integer': None,
                        'f_string': None,
                        # `ItemGeneralTwo(f_integer='10', f_float='20.30')`
                        # + nullables
                        'two_x_1': {
                            'item': {
                                'f_float': 20.3,
                                'f_integer': 10,
                                'one_1_x': {
                                    'bulk': [
                                        {
                                            'id': 2
                                        }
                                    ],
                                    'defaults': {}
                                },
                                'one_x_1': None,
                                'one_x_x': {
                                    'bulk': [],
                                    'defaults': {}
                                }
                            }
                        },
                        # already existed
                        'two_x_x': {
                            'bulk': [],
                            'defaults': {
                                'f_text': 'text-value'
                            }
                        }
                    }
                }
            ],
            'defaults': {
                'two_x_1': {
                    'item': {
                        'f_float': 20.3,
                        'f_integer': 10,
                        'one_x_1': None,
                        'one_x_x': {
                            'bulk': [],
                            'defaults': {}
                        }
                    }
                },
                'two_x_x': {
                    'bulk': [
                        {
                            'item': {
                                'f_integer': 20,
                                'one_x_1': None,
                                'one_x_x': {
                                    'bulk': [],
                                    'defaults': {}
                                }
                            }
                        },
                        {
                            'item': {
                                'f_float': 40.5,
                                'one_x_1': None,
                                'one_x_x': {
                                    'bulk': [],
                                    'defaults': {}
                                }
                            }
                        }
                    ],
                    'defaults': {}
                }
            }
        }
        self.assertTrue(bulk.to_dict(), expect)

    
    def test_can_create(self):
        self.setup_models()
        
        self.item_cls_manager.clear()
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'two_1_1', 'f_integer', 'f_string'}]
            getters = [{'f_integer', 'f_string'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
        
        # item one has creator field
        item_one = ItemGeneralOne(f_integer=10)
        self.assertFalse(item_one.can_create(fkeys={}))
        item_one['f_string'] = 'str-one'
        self.assertFalse(item_one.can_create(fkeys={}))
        
        # relation (using `True` as fake ORM model value)
        self.assertTrue(item_one.can_create(fkeys={'two_1_1': True}))
        
        # item two (empty creators)
        item_two = ItemGeneralTwo()
        # can create with all fields equal to `None`
        self.assertTrue(item_two.can_create(fkeys={}))
        item_two['f_integer'] = '1000'
        self.assertTrue(item_two.can_create(fkeys={}))
        
        # item one no fkey but has field
        item_one = ItemGeneralOne(f_integer=10, f_string='20',
                                  two_1_1=item_two)
        self.assertFalse(item_one.can_create(fkeys={}))


        # `model_cls is None`
        class TestItem(Item):
            pass
        self.assertIsNone(TestItem.model_cls)
        test_item = TestItem()
        self.assertFalse(test_item.can_create(fkeys={}))
    
    
    def test_contains(self):
        self.setup_models()
        item = self.ItemGeneralOne()
        item['f_integer'] = '1'
        item['two_1_x__f_integer'] = '2'
        bulk = item['two_1_x']
        bulk['one_x_x__f_integer'] = '3'
        
        self.assertIn('f_integer', item)
        self.assertIn('two_1_x__f_integer', item)
        self.assertIn('two_1_x__one_x_x__f_integer', item)  # from bulk
        
        self.assertNotIn('wrong_key', item)
        self.assertNotIn('wrong_key__f_integer', item)
        self.assertNotIn('two_1_x__one_x_x__wrong_key', item)
        
        self.assertIn('f_integer', bulk)  # item
        self.assertIn('one_x_x__f_integer', bulk)
        
        self.assertNotIn('wrong_key', bulk)
        self.assertNotIn('wrong_key__f_integer', bulk)
        self.assertNotIn('two_1_x__one_x_x__wrong_key', bulk)
        
        #--- aliased -----------------------------------------------------------
        self.setup_models(aliased=True)
        
        item = self.ItemGeneralOne()
        item['alias_1'] = '1'
        item['alias_2'] = '2'
        item['two_1_1__alias_1__post'] = 'str-1'
        item['two_1_1__alias_2__post'] = '3'
        item['two_1_1__alias_3__post'] = '4'
        bulk = item['two_1_x']
        bulk['alias_1__post'] = 'str-2'
        
        self.assertIn('alias_1', item)
        self.assertIn('alias_2', item)
        self.assertIn('two_1_1__alias_1__post', item)
        self.assertIn('two_1_1__alias_2__post', item)
        self.assertIn('two_1_1__alias_3__post', item)
        
        self.assertNotIn('wrong_key', item)
        self.assertNotIn('wrong_key__f_integer', item)
        self.assertNotIn('two_1_x__one_x_x__wrong_key', item)
        
        self.assertIn('alias_1__post', bulk)
        
        self.assertNotIn('wrong_key', bulk)
        self.assertNotIn('wrong_key__f_integer', bulk)
        self.assertNotIn('two_1_x__one_x_x__wrong_key', bulk)
        
    
    def test_auto_reverse_relations(self):
        class ItemAutoReverseOne(Item):
            model_cls = self.ModelAutoReverseOne
        
        class ItemAutoReverseTwoA(Item):
            model_cls = self.ModelAutoReverseTwoA
        
        class ItemAutoReverseTwoB(Item):
            model_cls = self.ModelAutoReverseTwoB
        
        class ItemAutoReverseThreeA(Item):
            model_cls = self.ModelAutoReverseThreeA
        
        class ItemAutoReverseThreeB(Item):
            model_cls = self.ModelAutoReverseThreeB
        
        class ItemAutoReverseFourA(Item):
            model_cls = self.ModelAutoReverseFourA
        
        class ItemAutoReverseFourB(Item):
            model_cls = self.ModelAutoReverseFourB


        for item_cls in (ItemAutoReverseOne,
                         ItemAutoReverseTwoA, ItemAutoReverseTwoB,
                         ItemAutoReverseThreeA, ItemAutoReverseThreeB,
                         ItemAutoReverseFourA, ItemAutoReverseFourB,):
            item_cls()  # completes relations
            relations_and_reverse = {}
            
            for key, relations in item_cls.relations.items():
                relations_and_reverse[key] = (
                    relations['reverse_key'],
                    relations['relation_type'],
                )
            
            self.assertEqual(relations_and_reverse,
                             item_cls.model_cls.ITEM_RELATIONS)

