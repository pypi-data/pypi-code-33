#!/usr/bin/env python

"""
    MHC prediction unit tests
    Created September 2015
    Copyright (C) Damien Farrell
"""

from __future__ import absolute_import, print_function
import sys, os
import pandas as pd
import unittest
from . import base, neo, analysis, sequtils, peptutils
pd.set_option('display.width', 120)

path = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.join(path, 'testing')

class NeoepitopeTests(unittest.TestCase):
    """Basic tests for neoepitope prediction"""

    def setUp(self):
        self.testdir = testdir
        if not os.path.exists(self.testdir):
            os.mkdir(self.testdir)
        return

    def test_workflow(self):
        """Test basic neoepitope workflow"""

        testalleles = ['HLA-A*02:02']
        v = neo.load_variants(os.path.join(testdir, 'input.vcf'))
        seqs = neo.get_mutant_sequences(variants=v, length=9)
        res = neo.predict_variants(seqs, alleles=testalleles, predictor='mhcflurry', cpus=1)
        #outfile = 'pvacseq_data/results_iedbmhc1.csv'
        #pvactest.to_csv(outfile, index=False)
        fcols=['pos', 'peptide', 'wt','name','variant_class','closest','self_mismatches','allele',
               'score','matched_score','binding_diff','binding_rank']
        res = res.sort_values('binding_rank')
        print (res[fcols])
        return

def run():
    unittest.main()

if __name__ == '__main__':
    unittest.main()
