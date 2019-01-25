#!/usr/bin/env python3
'''
Created on 5 nov. 2018

@author: jeanluc
'''
# from metaphor.test_monal.__main__ import run
# 
# run()
import unittest
import sys, os
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
try:
    from metaphor.test_monal.test_monal_module import TestMonalBase, TestMonal
    from metaphor.test_monal.test_data_manager import TestNdArrayBasedDataManager, TestOtherStyleBasedDataManager, TestCsvBasedDataManager
    from metaphor.test_monal.test_monaltoolbox import TestMonalToolbox
    from metaphor.test_monal.test_toolbox import TestToolbox
    from metaphor.test_monal.test_utils import TestUtils
    from metaphor.test_monal.test_linalg import TestLinAlg
    from metaphor.test_monal.test_property import TestProperty
    from metaphor.test_monal.test_libManager import TestLibManager
except ImportError:
    from test_monal_module import TestMonalBase, TestMonal
    from test_data_manager import TestNdArrayBasedDataManager, TestOtherStyleBasedDataManager, TestCsvBasedDataManager
    from test_monaltoolbox import TestMonalToolbox
    from test_toolbox import TestToolbox
    from test_utils import TestUtils
    from test_linalg import TestLinAlg
    from test_property import TestProperty
    from test_libManager import TestLibManager
     
def run():
    pth = os.getcwd()
    filepth = os.path.dirname(__file__)
    if pth in sys.path:
        filepth = os.path.join(pth, filepth)
    else:
        sys.path.append(pth)
    if not filepth in sys.path:
        sys.path.append(filepth)
    if filepth != pth:
        os.chdir(filepth)
    noLibArg = '--no-lib-test'
    DO_TEST_LIBMANAGER = not noLibArg in sys.argv
    if not  DO_TEST_LIBMANAGER:
        sys.argv.pop(sys.argv.index(noLibArg))
 
    if DO_TEST_LIBMANAGER:
        caselist = (TestMonalToolbox, 
                    TestUtils, 
                    TestToolbox,
                    TestNdArrayBasedDataManager,
                    TestOtherStyleBasedDataManager,
                    TestCsvBasedDataManager,
                    TestMonalBase,
                    TestMonal,
                    TestLinAlg,
                    TestProperty,
                    TestLibManager)
    else:
        caselist = (TestMonalToolbox, 
                    TestUtils, 
                    TestToolbox,
                    TestNdArrayBasedDataManager,
                    TestOtherStyleBasedDataManager,
                    TestCsvBasedDataManager,
                    TestMonalBase,
                    TestMonal,
                    TestLinAlg,
                    TestProperty)
         
         
    print("\n---- Test_monal ----")
    print("Python", sys.version)
    suite = unittest.TestSuite()
    for test_class in caselist:
        if test_class:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
    os.chdir(pth)

if __name__ == "__main__":
    run()
