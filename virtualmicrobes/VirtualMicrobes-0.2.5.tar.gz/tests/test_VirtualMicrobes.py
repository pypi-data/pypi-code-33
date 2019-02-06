'''
Created on Oct 2, 2016

@author: thocu
'''
import os
import shutil
import json
import datetime


print 'inside the test script for VirtualMicrobes'


class TestVirtualMicrobesBase(object):
    def setup_method(self, _):
        '''
        Do some setup for testing
        '''
        print 'In test setup'
        pass

    def teardown_method(self, _):
        '''
        Do the teardown for testing
        '''
        print 'in test teardown'
        pass


class TestSimStart(TestVirtualMicrobesBase):
    def test_init(self):
        print 'dummy init test'
        from VirtualMicrobes.simulation import Simulation
        assert 1 == 1
        
    