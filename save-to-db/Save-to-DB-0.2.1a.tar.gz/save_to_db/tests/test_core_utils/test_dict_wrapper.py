from save_to_db.core.item import Item
from save_to_db.utils.test_base import TestBase


class TestDictWrapper(TestBase):
    
    def test_wrap_and_get_item(self):
        
        class TestItem(Item):
            pass
        
        original_item = TestItem()
        dict_wrapper = original_item.dict_wrapper()
        returned_item = dict_wrapper.get_item()
        
        self.assertIs(returned_item, returned_item)