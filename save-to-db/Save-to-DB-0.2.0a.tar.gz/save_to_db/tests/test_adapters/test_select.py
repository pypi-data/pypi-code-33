from save_to_db.core.item import Item
from save_to_db.utils.test_base import TestBase



class TestSelect(TestBase):
    
    ModelGeneralOne = None
    ModelGeneralTwo = None
    
    def test_select(self):
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
                
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
        
        # single item fild
        item_one = ItemGeneralOne(f_integer=1, f_text='T-1')
        self.assertEqual(item_one.select('f_integer'),
                         [1])
        self.assertEqual(item_one.select('f_text'),
                         ['T-1'])
        self.assertEqual(item_one.select('f_string'),
                         [])
        
        # select from related single item
        item_one = ItemGeneralOne()
        item_one['two_x_1'](f_text='T-1')
        self.assertEqual(item_one.select('two_x_1__f_text'),
                         ['T-1'])
        self.assertEqual(item_one.select('two_x_1__f_string'),
                         [])
        self.assertEqual(item_one.select('two_x_1'),
                         [item_one['two_x_1']])
        
        # select from bulk item
        item_bulk = ItemGeneralOne.Bulk()
        item_bulk.gen(f_integer=1, f_text='T-1')
        item_bulk.gen(f_integer=2)
        item_bulk.gen(f_text='T-3')
        item_bulk.gen(f_float=4.0)
        
        self.assertEqual(item_bulk.select('f_integer'),
                         [1, 2])
        self.assertEqual(item_bulk.select('f_text'),
                         ['T-1', 'T-3'])
        
        # select from many bulks
        top_item_bulk = ItemGeneralOne.Bulk()
        for middle_item_no in range(3):
            middle_item = top_item_bulk.gen(
                f_integer=middle_item_no, f_string='middle-{}'.format(middle_item_no))
            item_bulk = middle_item['two_x_x']
            for item_no in range(2):
                item_bulk.gen(f_integer=middle_item_no, f_float=item_no,
                              f_string='P-{}, I-{}'.format(middle_item_no,
                                                           item_no))
        
        self.assertEqual(top_item_bulk.select('f_string'),
                         ['middle-0', 'middle-1', 'middle-2'])
        self.assertEqual(top_item_bulk.select('two_x_x__f_string'),
                         ['P-0, I-0', 'P-0, I-1',
                          'P-1, I-0', 'P-1, I-1',
                          'P-2, I-0', 'P-2, I-1'])
        self.assertEqual(top_item_bulk.select('two_x_x'),
                         [top_item_bulk.bulk[0]['two_x_x'],
                          top_item_bulk.bulk[1]['two_x_x'],
                          top_item_bulk.bulk[2]['two_x_x']])
        
        
        