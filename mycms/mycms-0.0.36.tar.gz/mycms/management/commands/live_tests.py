import unittest
import mycms
from . import  tests_classes


from django.core.management.base import BaseCommand, CommandError
from mycms.models import CMSEntries

import shutil, tempfile
from os import path
import unittest

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned

from mycms.view_handlers.page_types import singlepageview_pagetype_obj
from mycms.view_handlers.page_types import multipageview_pagetype_obj
from mycms.view_handlers.page_types import allarticles_pagetype_obj


class TestExample(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_something(self):
        # Create a file in the temporary directory
        f = open(path.join(self.test_dir, 'test.txt'), 'w')
        # Write something to it
        f.write('The owls are not what they seem')
        # Reopen the file and check if what we read back is the same
        f = open(path.join(self.test_dir, 'test.txt'))
        self.assertEqual(f.read(), 'The owls are not what they seem')

import sys
class Command(BaseCommand):

    """
    Example on how to create and run a unittest from within the django 
    management commands. 
    """
    def add_arguments(self, parser):
        parser.add_argument('--test_classes', nargs='+', type=str)
   

    def handle(self, *args, **options):
        
        suite = unittest.TestSuite()        
        test_class_names =  options.get("test_classes", None)
        
        if test_class_names: 
        
            for test_class in test_class_names: 
                print(test_class)
                suite.addTest(unittest.defaultTestLoader.loadTestsFromName(test_class, 
                module=tests_classes))
                
                
            unittest.TextTestRunner().run(suite)
                    
        