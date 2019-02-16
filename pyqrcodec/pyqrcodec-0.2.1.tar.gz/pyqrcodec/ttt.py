#! /usr/bin/python
#
__all__=["Method"]

import unittest

def Method(matrix):
    assert matrix and matrix[0]

    h, w, area = len(matrix), len(matrix[0]), 0
    map(lambda x:len(x)-w and 1/0, matrix)  # a matrix is expected, whose
                                            # every row with the same length

    vertAccu = [0]*(w+1)
    for i in xrange(h):
        stack = []
        for j in xrange(w+1):
            vertAccu[j] = 0 if w == j or not matrix[i][j] else vertAccu[j]+1

        for j in xrange(w+1):
            while stack and vertAccu[stack[-1]] > vertAccu[j]:
                # notice: the following statement is very concise, and don't 
                # modify it, unless you know what does this mean exactly.
                l = vertAccu[stack.pop()] * (j-(stack[-1]+1 if stack else 0))
                if l > area:
                    area = l
            
            stack.append(j);
    return area


class Testing(unittest.TestCase):
    
    def single(self, r, matrix):
        self.assertEqual(Method(matrix), r)
    def test_4(self):
        self.single(4, [
    [1,1],
    [1,1]])
        self.single(4, [
    [1,1],
    [1,1],
    [0,1],
    [1,0]])
        self.single(4, [
    [1,1,0],
    [1,1,1],
    [0,1,0]])
    def test_6(self):
        self.single(6, [
    [1,1,1,0,1,1],
    [0,1,0,0,0,1],
    [0,1,1,1,1,1],
    [0,1,1,1,0,1],
    [0,1,0,0,1,1],
])
    def test_8(self):
        self.single(8, [
    [1,1,1,0,1,1],
    [0,1,1,0,0,1],
    [0,1,1,1,1,1],
    [0,1,1,1,0,1],
    [0,1,0,0,1,1],
])  

    
if __name__ == "__main__":
    unittest.main()