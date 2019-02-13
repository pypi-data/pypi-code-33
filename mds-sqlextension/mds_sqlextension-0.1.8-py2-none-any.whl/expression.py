# -*- coding: utf-8 -*-


from sql import Expression, Flavor

__all__ = ['Overlaps']


class Overlaps(Expression):
    __slots__ = ('start1', 'end1', 'start2', 'end2')

    def __init__(self, start1, end1, start2, end2):
        super(Overlaps, self).__init__()
        self.start1 = start1
        self.end1 = end1
        self.start2 = start2
        self.end2 = end2

    def __str__(self):
        if isinstance(self.start1, Expression):
            start1 = self.start1
        else:
            start1 = Flavor.get().param
        
        if isinstance(self.end1, Expression):
            end1 = self.end1
        else:
            end1 = Flavor.get().param
        
        if isinstance(self.start2, Expression):
            start2 = self.start2
        else:
            start2 = Flavor.get().param
        
        if isinstance(self.end2, Expression):
            end2 = self.end2
        else:
            end2 = Flavor.get().param
        
        return '(%s, %s) OVERLAPS (%s, %s)' % (start1, end1, start2, end2)

    @property
    def params(self):
        l1 = []
        if not isinstance(self.start1, Expression):
            l1.append(self.start1)
        else :
            l1.extend(self.start1.params)
        
        if not isinstance(self.end1, Expression):
            l1.append(self.end1)
        else :
            l1.extend(self.end1.params)
        
        if not isinstance(self.start2, Expression):
            l1.append(self.start2)
        else :
            l1.extend(self.start2.params)
        
        if not isinstance(self.end2, Expression):
            l1.append(self.end2)
        else :
            l1.extend(self.end2.params)
        return tuple(l1)
