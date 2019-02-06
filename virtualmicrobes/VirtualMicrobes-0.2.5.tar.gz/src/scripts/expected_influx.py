#! /usr/bin/env python
# encoding: utf-8

'''
Created on Aug 16, 2016

@author: thocu
'''



import math
import sys
def expected_value(base, domain):
    '''
    calculates the expected value of a log-uniformly distributed random
    variable with *base* and *domain* .
    
    This is the mean of the integral of base^x with U(x) a uniform
    distribution on the given domain.
    '''
    m,n = domain
    if m > n:
        m,n = n,m
    elif m == n:
        return base ** m
    return 1./(n - m) * ( base ** n / math.log(base) - base ** m / math.log(base) ) 

if __name__ == '__main__':
    base, domain = float(sys.argv[1]), sys.argv[2]
    deg_rate = float(sys.argv[3])
    m,n = map(float, domain.split(','))
    expected = expected_value(base,(m,n))
    print expected/deg_rate