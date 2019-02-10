import unittest
from mycms.models import CMSEntries

from mycms.view_handlers.category_page import CategoryPage
from mycms.view_handlers.page_types import singlepageview_pagetype_obj
from mycms.view_handlers.page_types import multipageview_pagetype_obj
from mycms.view_handlers.page_types import allarticles_pagetype_obj

class CategoryPageTests(unittest.TestCase):
    
    
    def setUp(self):
        print("loaded {}".format(self.__class__.__name__))


    def test_all_sub_articles(self):
        
        #tests getting all sub articles of a particular category page
        page_object = CMSEntries.objects.get(path__path="/sysadmin/linux")
        
        x = CategoryPage(page_object)
        print("*"*80)
        for i in x.all_sub_articles():
            print(i.title)
            
    def test_categories(self):
        
        page_object = CMSEntries.objects.get(path__path="/sysadmin/linux")
        x = CategoryPage(page_object)        
        
        for i in x.categories:
            print(i.title)