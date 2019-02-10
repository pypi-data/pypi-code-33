from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from mycms import wingdbstub
#Imports
import unittest
import mock 

from random import randint
import loremipsum


#Django Imports
from django.test import TestCase
from django.template.defaultfilters import slugify
from django.http import HttpRequest
#Local Application Imports

import mycms
from mycms import exceptions
from mycms import pageview
from mycms.models import Pages
from mycms.models import Paths
from mycms import YACMS_BASE_URL

from django.conf import settings

class ModelTests(unittest.TestCase):
    
    
    def test_can_create_default_base_path(self):
        """Ensure that we can create a base path, where entry 
        is at / and has no parent"""
        
        #In order to be able to do this test, we need to delete all the 
        #Paths 
        
        for entry in Pages.objects.all():
            entry.delete()
            
        for entry in Paths.objects.all():
            entry.delete()
        
        
        path_instance = Paths()
        path_instance.save()
        self.assertEqual(path_instance.path, "/")
        
    def test_can_create_root_path(self):
        """Ensure we can create a basic Path entry"""
        
        path_instance = Paths(path="/sysadmin")
        path_instance.save()
         
        retrieved_path_instance = Paths.objects.get(path="/sysadmin")
        self.assertEqual(retrieved_path_instance, path_instance)
        
         
    def test_can_create_parent_paths_recursively(self):
        
        path_instance = Paths(path="/foo/bar/baz")
        path_instance.save()
        
        foo_bar_baz = Paths.objects.get(path="/foo/bar/baz")
        foo_bar = Paths.objects.get(path="/foo/bar")
        foo = Paths.objects.get(path="/foo")
        
        self.assertEqual(foo_bar_baz.path, "/foo/bar/baz")
        self.assertEqual(foo_bar.path, "/foo/bar")
        self.assertEqual(foo.path, "/foo")
        
        
    def test_can_create_a_page_entry(self):
        """
        Ensure that given a path, we can create a page. This test
        provides all the required values. 
        """
        
        path_instance = Paths(path="/this/is/a/test/article")
        path_instance.save()
        
        page_instance = Pages()

        page_values = { "title" :"This is the title", 
                        "content": "This is just some content.",
                        "page_type": "HTMLPAGE",
                        "template": "index.html",
                        "frontpage": True,
                        "published": True,
                        "meta_description": "This is the meta description.",
                        "article_logo": "fedora-logo.png"}

        
        page_instance.path = path_instance
        page_instance.title = page_values.get("title")
        page_instance.slug = slugify(page_values.get("title"))
        page_instance.content = page_values.get("content")
        page_instance.page_type = page_values.get("page_type")
        page_instance.template = page_values.get("template")
        page_instance.frontpage =  page_values.get("frontpage")
        page_instance.published = page_values.get("published")
        page_instance.meta_description = page_values.get("meta_description")
        page_instance.article_logo = page_values.get("article_logo")
        page_instance.save()
        
        #The use cases is to load by path so we try to do the same here. 
        page_instance_from_db = Pages.objects.get(path=path_instance)
        
        #Now ensure that everything was saved properly.
        for key in page_values.keys():        
            page_value = page_values.get(key)
            db_value = getattr(page_instance_from_db, key) 
            print("Comparing \t'{}' \t: \t db '{}'".format(page_value, db_value))
            self.assertEqual(page_value, db_value)
            
            
            
    def test_can_create_a_page_with_default_values_via_save_override(self):
        """
        This test creates a page given a minimum amount of values. 
        """
        
        
        path_instance = Paths(path="/this/is/a/test/mimimal_article")
        path_instance.save()
        
        page_instance = Pages()

        page_values = { "title" :"This is the title", 
                        "content": "This is just some content.",
                        "page_type": "HTMLPAGE",
                        "template": "index.html",
                        "frontpage": True,
                        "published": True,
                        "meta_description": "This is the meta description.",
                        "article_logo": "fedora-logo.png"}
        
        page_instance.path = path_instance
        page_instance.title = page_values.get("title")
        #Do not set the slug because it should be filled automatically
        #page_instance.slug = slugify(page_values.get("title"))
        page_instance.content = page_values.get("content")
        page_instance.page_type = page_values.get("page_type")
        #Do not set the template because ave should fill it in automatically
        #page_instance.template = page_values.get("template")
        page_instance.frontpage =  page_values.get("frontpage")
        page_instance.published = page_values.get("published")
        page_instance.meta_description = page_values.get("meta_description")
        page_instance.article_logo = page_values.get("article_logo")
        page_instance.save()
           
        print(page_instance.slug)
        
        self.assertEqual(page_instance.slug, slugify(page_values.get("title")))
        self.assertEqual(page_instance.template, "{}.html".format(page_instance.page_type.lower()))
        
        
        
class ExtendedModelTests(unittest.TestCase):
    """Test the rest of the attributes."""
    
    def setUp(self):
        """Create a base url"""
        self.path_inst = Paths(path="/articles/my-test-article")
        self.path_inst.save()
        
        page = Pages()
        
        page.path = self.path_inst
        page.title = "My Test Article"
        page.content = "This is just a dummy content"
        page.page_type = "HTMLVIEW"
        page.frontpage = True
        page.published = True
        page.meta_description = ""
        page.save()
        
        self.page_instance = page
        
    
    def test_get_absoloute_url(self):
        """Tests to show that we can get a correct absolute URL."""
        #Ensure that we can get a correct absolute URL 
        
        #Override the settings.YACMS_BASE_URL with our value
       
        url = self.page_instance.get_absolute_url()
        expected_url = "/{}{}".format(mycms.YACMS_BASE_URL,self.page_instance.path.path.lstrip("/"))
        self.assertEqual(url, expected_url) 
    
    
    #def test_introduction(self):
        #self.fail()
        
        
    #def test_logo(self):
        #self.fail()
        
        
    #def test_data_dict(self):
        #self.fail()
        
    #def test_view(self):
        #"""A simple test to show that view returns a PageView. This will 
        #fail if something is wrong with the pageview module which has its 
        #own set of tests."""
        #self.fail()
    
    
    

    
         
         
        
        
        
        
        
        