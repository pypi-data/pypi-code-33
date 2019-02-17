# -*- coding: utf-8 -*-

import unittest
import os

from errorcalcs import add, calc

class TestNumberMethods(unittest.TestCase):

    def testumath(self):
        formel_erg = [
                ('log(x)', '-0.3566749+/-0.0045714'),
                ('log10(x)', '-0.1549020+/-0.0019853'),
                ('log(x)*y', '-1.541357+/-0.054697'),
                ('sin(x)', '0.6442177+/-0.0024475'),
                ('cos(y)', '-0.38105+/-0.13221'),
                ('tan(z)', '0.0097+/-7.6007'),
                ('cos(x-y)', '-0.887056+/-0.066034'),
                ('tan(y*0.0001*z**x)', '0.230722+/-0.010452'),
                ('sqrt(y)', '2.078812+/-0.034395'),
                ('log(-x)', 'error'),
                ('x/0', 'error'),
                ('z*0', '  0.0+/-0'),
                ('-x**y', '-0.214090+/-0.011710'),
                ('x**y', '0.214090+/-0.011710'),
                ('-x*1/100*z', '-53.79042+/-0.25159')
                  ]
        for i in formel_erg:
            formel_datei = open('.__log__/formel.txt', 'w')
            print(i[0], file = formel_datei)
            formel_datei.close()
            var, value, error, formel = add.get_ins()
            ergebnis, formel = calc.calculate(var, value, error, formel)
            self.assertEqual(str(ergebnis), i[1])
        

def main():
    var = ['x', 'y', 'z']
    value = ['0.7', '4.32146', '7684.3453']
    error = ['0.0032', '0.143', '7.6']
    var_datei = open('.__log__/var.txt', 'w')
    value_datei = open('.__log__/value.txt', 'w')
    error_datei = open('.__log__/error.txt', 'w')
    for i in var:
        print(i, file = var_datei)
    for i in value:
        print(i, file = value_datei)
    for i in error:
        print(i, file = error_datei)
    var_datei.close()
    value_datei.close()
    error_datei.close()
    
    unittest.main()

if __name__ == '__main__':
    try:
        os.mkdir('.__log__')
    except FileExistsError:
        pass
    main()
