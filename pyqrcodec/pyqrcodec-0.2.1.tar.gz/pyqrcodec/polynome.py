#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2014年7月22日

@author: zhouzhichao
'''
from bitutil import makeBits2String, bit2char, bool2char, char2bool

class Polynome(object):
    '''
        布尔多项式类
    '''
    __solts__ = ['__rates']
    def __init__(self, **kwargs):
        order = kwargs.get('order')
        # length = kwargs.get('length', 0)
        value = kwargs.get('value')
        if not order or order < 0: order = 0

        if value is None:
            self.__rates = [False] * order
        else:
            self.assign(value)
    def assign(self, value):
        value = makeBits2String(value)
        if value is None:
            return
        self.__rates = map(char2bool, value)
        self.__rates.reverse()
    def mul(self, poly):
        '''
            多项式乘法
        '''
        so, po = self.order, poly.order
        result = Polynome(order=so+po-1)
        for i in xrange(po):
            if not poly.__rates[i]: 
                continue
            for j in xrange(so):
                result.__rates[i] ^= self.__rates[j]
                i += 1 
        return result
    def clone(self):
        poly = Polynome()
        poly.__rates = map(lambda x:x, self.__rates)
        return poly
    def mod(self, poly):
        '''
            多项式取模
        '''
        if not isinstance(poly, Polynome):
            poly = Polynome(value=poly)
        so, po = self.order, poly.order
        if po == 0:
            raise Exception('Polynome divided by zero')
        if so < po:
            return self.clone()
        memory = map(lambda x: x, self.__rates[:so])
        
        assert memory[-1]
        top, genlen = so, po

        while top >= genlen:
            for i in xrange(genlen):
                memory[top-i-1] ^= poly.__rates[genlen-i-1]
            
            for i in xrange(1,so):
                if memory[-i]:
                    top = so-i+1
                    break
            if not memory[top-1]:
                break
        
        for i in xrange(len(memory)):
            if memory[-1-i]:
                top = len(memory)-i
                break

        ret = Polynome()
        ret.__rates = memory[:top]
        return ret
    @property
    def value(self):
        '''
            多项式的索引值属性（只读）
        '''
        value, key = 0, 1
        for i in self.__rates:
            if i: value += key
            key <<= 1
        return value
    @property
    def order(self):
        '''
            多项式的秩属性（只读）
        '''
        if len(self.__rates) <= 0:
            return 0
        for i in xrange(len(self.__rates)):
            if self.__rates[-1-i]:
                return len(self.__rates)-i
        return 0
    def printf(self, **kFormat):
        if kFormat.get('polynome') and not kFormat.get('binary'):
            result = []
            for i in xrange(len(self.__rates)):
                if self.__rates[i]:
                    result.append('x^%s'%i)
            if not kFormat.get('desc'): result.reverse()
            return '+'.join(result)
        else:
            result = (''.join(map(bool2char, self.__rates)))
            if not kFormat.get('desc'): result = result[::-1]
            return result