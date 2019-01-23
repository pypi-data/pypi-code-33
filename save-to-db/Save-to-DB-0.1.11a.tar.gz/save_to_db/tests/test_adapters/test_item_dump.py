import datetime
from io import BytesIO
from save_to_db.core.item import Item
from save_to_db.utils.test_base import TestBase



class TestItemDump(TestBase):
    """ Contains tests for converting items into `bytes` objects and back.
    Also tests saving items to and loading items from files.  
    """

    ModelGeneralOne = None
    ModelGeneralTwo = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        class ItemFieldTypes(Item):
            model_cls = cls.ModelFieldTypes
        cls.ItemFieldTypes = ItemFieldTypes
        
        class ItemGeneralOne(Item):
            model_cls = cls.ModelGeneralOne
        cls.ItemGeneralOne = ItemGeneralOne
        
        class ItemGeneralTwo(Item):
            model_cls = cls.ModelGeneralTwo
        cls.ItemGeneralTwo = ItemGeneralTwo
    
    
    def check_dumps(self, item, expected):
        # converting to bytes
        item_as_bytes = self.persister.dumps(item)
        self.assertIsInstance(item_as_bytes, bytes)
        
        item = self.persister.loads(item_as_bytes)        
        self.assertEqual(item.to_dict(), expected)
        
        # saving to a file-like object        
        storage = BytesIO()
        self.persister.dump(item, storage)
    
        storage.seek(0)
        item = self.persister.load(storage)
        self.assertEqual(item.to_dict(), expected)
    
    
    def test_dump_types(self):
        item = self.ItemGeneralOne(f_binary='binary data',
                                   f_boolean='true',
                                   f_string='string data',
                                   f_text='text_data',
                                   f_integer='10',
                                   f_float='10.10',
                                   f_date='2000-10-30',
                                   f_time='20:30:40',
                                   f_datetime='2000-10-30 20:30:40')
        expected = {
            'item': {
                'f_binary': b'binary data',
                'f_boolean': True,
                'f_date': datetime.date(2000, 10, 30),
                'f_datetime': datetime.datetime(2000, 10, 30, 20, 30, 40),
                'f_float': 10.1,
                'f_integer': 10,
                'f_string': 'string data',
                'f_text': 'text_data',
                'f_time': datetime.time(20, 30, 40),
            }
        }
        self.check_dumps(item, expected)


    def test_dump_single_item_with_relations(self):
        item = self.ItemGeneralOne(f_integer='1')
        item['two_1_1__f_integer'] = '11'
        item['two_x_x'].gen(f_float='99.1')
        item['two_x_x'].gen(f_float='99.2', one_x_1__f_integer='192') 
        item['two_x_x__f_float'] = '1000.1'
        
        expected = {
            'id': 1,
            'item': {
                'f_integer': 1,
                'two_1_1': {
                    'item': {
                        'f_integer': 11,
                        'one_1_1': {
                            'id': 1
                        }
                    }
                },
                'two_x_x': {
                    'bulk': [
                        {
                            'item': {
                                'f_float': 99.1,
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
                            'id': 2,
                            'item': {
                                'f_float': 99.2,
                                'one_x_1': {
                                    'item': {
                                        'f_integer': 192,
                                        'two_1_x': {
                                            'bulk': [
                                                {
                                                    'id': 2
                                                }
                                            ],
                                            'defaults': {}
                                        }
                                    }
                                },
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
                        'f_float': 1000.1
                    }
                }
            }
        }
        self.check_dumps(item, expected)
        
        
    def test_dump_bulk_item_with_relations(self):
        bulk = self.ItemGeneralOne.Bulk()
        bulk.gen(f_float='1.1')
        bulk.gen(f_float='1.2', two_x_1__f_integer='2') 
        bulk['two_x_x__f_float'] = '1000.1'
        bulk['two_x_1'] = self.ItemGeneralTwo(f_boolean='true')
        
        expected = {
            'bulk': [
                {
                    'id': 1,
                    'item': {
                        'f_float': 1.1,
                        'two_x_1': {
                            'item': {
                                'f_boolean': True,
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
                                'f_float': 1000.1
                            }
                        }
                    }
                },
                {
                    'id': 2,
                    'item': {
                        'f_float': 1.2,
                        'two_x_1': {
                            'item': {
                                'f_integer': 2,
                                'one_1_x': {
                                    'bulk': [
                                        {
                                            'id': 2
                                        }
                                    ],
                                    'defaults': {}
                                }
                            }
                        },
                        'two_x_x': {
                            'bulk': [],
                            'defaults': {
                                'f_float': 1000.1
                            }
                        }
                    }
                }
            ],
            'defaults': {
                'two_x_1': {
                    'item': {
                        'f_boolean': True
                    }
                },
                'two_x_x__f_float': 1000.1
            }
        }

        self.check_dumps(bulk, expected)
    
    
    def test_multiple_items_dump(self):
        storage = BytesIO()
        
        self.persister.dump(self.ItemGeneralOne(f_integer='1'), storage)
        self.persister.dump(self.ItemGeneralOne(f_integer='2'), storage)
        self.persister.dump(self.ItemGeneralOne(f_integer='3'), storage)
        
        storage.seek(0)
        
        dict_wrapper = self.persister.load(storage).to_dict()
        self.assertEqual(dict_wrapper, {'item': {'f_integer': 1}})
        
        dict_wrapper = self.persister.load(storage).to_dict()
        self.assertEqual(dict_wrapper, {'item': {'f_integer': 2}})
        
        dict_wrapper = self.persister.load(storage).to_dict()
        self.assertEqual(dict_wrapper, {'item': {'f_integer': 3}})
        
        # no more items
        dict_wrapper = self.persister.load(storage)
        self.assertIsNone(dict_wrapper)


    def test_arbirary_id_position(self):
        # normal item
        item_one = self.ItemGeneralOne(f_integer='1')
        child_item = item_one['child_1_x'].gen(f_integer='2')
        item_one['child_x_x'].add(child_item)
        item_one.process()
        expect = {
            'id': 1,
            'item': {
                'child_1_x': {
                    'bulk': [
                        {
                            'id': 2,
                            'item': {
                                'f_integer': 2,
                                'parent_x_1': {
                                    'id': 1
                                },
                                'parent_x_x': {
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
                },
                'child_x_x': {
                    'bulk': [
                        {
                            'id': 2
                        }
                    ],
                    'defaults': {}
                },
                'f_integer': 1
            }
        }
        loaded_item = self.ItemGeneralOne().load_dict(expect)
        self.assertEqual(loaded_item.to_dict(), expect)
        
        # moving parent data
        item_as_dict = {
            'id': 1,
            'item': {
                'child_1_x': {
                    'bulk': [
                        {
                            'id': 2
                        }
                    ],
                    'defaults': {}
                },
                'child_x_x': {
                    'bulk': [
                        {
                            'id': 2,
                            'item': {
                                'f_integer': 2,
                                'parent_x_1': {
                                    'id': 1
                                },
                                'parent_x_x': {
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
                },
                'f_integer': 1
            }
        }
        loaded_item = self.ItemGeneralOne().load_dict(item_as_dict)
        self.assertEqual(loaded_item.to_dict(), expect)
        
        # id in default
        item_one = self.ItemGeneralOne.Bulk()
        item_one.gen(f_integer='1')
        other_item = item_one.gen(f_integer='2')
        item_one['parent_x_1'] = other_item
        item_one.process()
        expect = {
            'bulk': [
                {
                    'id': 2,
                    'item': {
                        'f_integer': 1,
                        'parent_x_1': {
                            'item': {
                                'child_1_x': {
                                    'bulk': [
                                        {
                                            'id': 2
                                        }
                                    ],
                                    'defaults': {}
                                },
                                'f_integer': 2
                            }
                        }
                    }
                },
                {
                    'id': 1
                }
            ],
            'defaults': {
                'parent_x_1': {
                    'id': 1,
                    'item': {
                        'f_integer': 2,
                        'parent_x_1': {
                            'item': {
                                'child_1_x': {
                                    'bulk': [
                                        {
                                            'id': 1
                                        }
                                    ],
                                    'defaults': {}
                                },
                                'f_integer': 2
                            }
                        }
                    }
                }
            }
        }
        loaded_item = self.ItemGeneralOne.Bulk().load_dict(expect)
        self.assertEqual(loaded_item.to_dict(), expect)
        
        # moving other item data
        item_as_dict = {
            'bulk': [
                {
                    'id': 2,
                    'item': {
                        'f_integer': 1,
                        'parent_x_1': {
                            'item': {
                                'child_1_x': {
                                    'bulk': [
                                        {
                                            'id': 2
                                        }
                                    ],
                                    'defaults': {}
                                },
                                'f_integer': 2
                            }
                        }
                    }
                },
                {
                    'id': 1,
                    'item': {
                        'f_integer': 2,
                        'parent_x_1': {
                            'item': {
                                'child_1_x': {
                                    'bulk': [
                                        {
                                            'id': 1
                                        }
                                    ],
                                    'defaults': {}
                                },
                                'f_integer': 2
                            }
                        }
                    }
                }
            ],
            'defaults': {
                'parent_x_1': {
                    'id': 1,
                  }
            }
        }
        loaded_item = self.ItemGeneralOne.Bulk().load_dict(item_as_dict)
        self.assertEqual(loaded_item.to_dict(), expect)