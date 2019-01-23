from save_to_db.core.item import Item
from save_to_db.utils.test_base import TestBase



class TestBulkSlicing(TestBase):
    """ Tests for bulk item slicing. """
    
    
    ModelGeneralOne = None
    ModelGeneralTwo = None
    
    def test_bulk_item_slice(self):
        
        class ItemsGeneralOne(Item):
            model_cls = self.ModelGeneralOne
                
        class ItemsGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
                
        
        bulk = ItemsGeneralOne.Bulk()
        bulk['f_string'] = 'str-value'
        
        items = []
        for i in range(10):
            item = ItemsGeneralOne(f_integer=i)
            items.append(item)
            bulk.add(item)
        
        first_slice = bulk.slice(0, 5)
        self.assertEqual(items[:5], first_slice.bulk)
        self.assertEqual(first_slice['f_string'], 'str-value')
        
        first_slice['f_text'] = 'text-value'
        self.assertNotIn('f_text', bulk)
        
        second_slice = bulk.slice(start=0, step=2)
        self.assertEqual(items[0::2], second_slice.bulk)
        self.assertEqual(second_slice['f_string'], 'str-value')
        
        bulk['f_float'] = '10.10'
        self.assertNotIn('f_float', second_slice)