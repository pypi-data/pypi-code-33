#-*- coding: ISO-8859-15 -*-

from metaphor.monal.Property import Property 
import unittest

class MyClass(object):
    
    def __init__(self):
        self._value = "My Property"
        self._values = list(range(10))
        
    def __enter__(self):
        return self
    def __exit__(self, atype, value, traceback):
        #del self
        pass
    
    @Property
    def myProp(self):
        return self._value
    
    @myProp.setter
    def myProp(self, value):
        self._value = value
        
    @Property
    def myVectorProp(self, index):
        return self._values[index]
    
    @myVectorProp.setter
    def myVectorProp(self, index, value):
        self._values[index] = value
        
    @myVectorProp.lengetter
    def myVectorProp(self):
        return len(self._values)
    
    @myVectorProp.lensetter
    def myVectorProp(self, value):
        self._values = list(range(value))
        
class TestProperty(unittest.TestCase):
    
    def testGetter(self):
        with MyClass() as aaa:
            self.assertEqual(aaa.myProp, "My Property")
        
    def testSetter(self):
        with MyClass() as aaa:
            aaa.myProp = "Your Property"
            self.assertEqual(aaa.myProp, "Your Property")
        
    def testGetterVector(self):
        with MyClass() as aaa:
            self.assertEqual(aaa.myVectorProp[5], 5)
            self.assertEqual(aaa.myVectorProp[7], 7)
            self.assertEqual(aaa.myVectorProp[8], 8)
            self.assertEqual(aaa.myVectorProp[-1], 9)
            self.assertEqual(aaa.myVectorProp[-2], 8)
        
    def testGetterVector2(self):
        with MyClass() as bbb:
            self.assertEqual(bbb.myVectorProp[8], 8)
        
    def testSetterVector(self):
        with MyClass() as aaa:
            self.assertEqual(aaa.myVectorProp[5], 5)
            aaa.myVectorProp[5] = 15
            self.assertEqual(aaa.myVectorProp[5], 15)
            
    def testGetLen(self):
        with MyClass() as aaa:
            self.assertEqual(aaa.myVectorProp.__len__(), 10)
            bbb = MyClass()
            for i in range(aaa.myVectorProp.count):
                self.assertEqual(aaa.myVectorProp[i], bbb.myVectorProp[i])
            for vala, valb in zip(aaa.myVectorProp, bbb.myVectorProp):
                self.assertEqual(vala, valb)
      
    def testSetLen(self):
        with MyClass() as aaa:
            aaa.myVectorProp.__setlen__(5) 
            self.assertEqual(aaa.myVectorProp.__len__(), 5)
            
    def testSlice(self):
        with MyClass() as aaa:
            self.assertEqual(aaa.myVectorProp[3:5] , [3,4])
            
def run():
    unittest.main (argv=("", "-v")) 
        
if __name__ == "__main__": 
    run()
      