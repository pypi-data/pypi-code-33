#!/usr/bin/env python3
'''
Created on 5 nov. 2018

@author: jeanluc
'''
import unittest
import sys, os
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

try:
    from metaphor.test_chem_gm.test_cycles import TestCycles
    from metaphor.test_chem_gm.test_GMmodel import Test_TokenList
    from metaphor.test_chem_gm.test_molecule import TestMolecule
    from metaphor.test_chem_gm.test_phenol_smiles import Test_Stability_smiles
    from metaphor.test_chem_gm.test_smiparser import Test_TokenList as Test_TokenList_smi
    from metaphor.test_chem_gm.test_stability_smiles import Test_Stability_smiles2
    from metaphor.test_chem_gm.test_token import Test_Token
except ImportError:
    from test_cycles import TestCycles
    from test_GMmodel import Test_TokenList
    from test_molecule import TestMolecule
    from test_phenol_smiles import Test_Stability_smiles
    from test_smiparser import Test_TokenList as Test_TokenList_smi
    from test_stability_smiles import Test_Stability_smiles2
    from test_token import Test_Token
    
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
    
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

    caselist = (TestCycles, 
                Test_TokenList, 
                TestMolecule, 
                Test_Stability_smiles,
                Test_TokenList_smi, 
                Test_Stability_smiles2, 
                Test_Token, )
    
    print("\n---- Test_chem_gm ----")
    print("Python", sys.version)
    suite = unittest.TestSuite()
    for test_class in caselist:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
    os.chdir(pth)
    
if __name__ == "__main__":
    run()
