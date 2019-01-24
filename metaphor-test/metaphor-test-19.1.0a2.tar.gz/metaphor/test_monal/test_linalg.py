#
# Copyright 2016 Jean-Luc PLOIX
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import numpy as np
import metaphor.monal.specialmath as sp
import unittest

class TestLinAlg(unittest.TestCase):
    
    def testLeverages(self):
        a = np.random.randn(6,4)
        U, s, V = np.linalg.svd(a, full_matrices=False)
        W = np.diag(s)
        
        res = np.dot(np.dot(U, W), V)
        fisher = np.dot(np.dot(V.T, np.diag(s**-2)), V)
        n, q = a.shape
        leverages = np.zeros((n,))
        for i in range(n):
            leverages[i] = sp.leverage(a[i], fisher)
            
        leverages2 = np.array([sp.leverage(ai, fisher) for ai in a])
        for val1, val2 in zip(leverages, leverages2):
            assert val1==val2

def run():
    unittest.main()

if __name__ == "__main__":
    run()
#     a = np.random.randn(6,4)
#     print(a.shape)
#     
#     U, s, V = np.linalg.svd(a, full_matrices=False)
#     
#     W = np.diag(s)
#     
#     print(U.shape, W.shape, V.shape)
#     #print U
#     
#     res = np.dot(np.dot(U, W), V)
#     #print a
#     #print res
#     
#     #ztz = np.dot(a.T, a)
#     #fisher = np.linalg.inv(ztz)
#     
#     fisher = np.dot(np.dot(V.T, np.diag(s**-2)), V)
#     n, q = a.shape
#     leverages = np.zeros((n,))
#     for i in range(n):
#         leverages[i] = sp.leverage(a[i], fisher)
#         
#     leverages2 = np.array([sp.leverage(ai, fisher) for ai in a])
#     
#     #print fisher
#     print(leverages, np.sum(leverages))
#     print(leverages2, np.sum(leverages2))
#     for val1, val2 in zip(leverages, leverages2):
#         assert val1==val2
#         
#     print "Done"
#     
#     #leverages2 = (a.dot(fisher)).dot(a.T)
#     #print leverages2, np.trace(leverages2)
    