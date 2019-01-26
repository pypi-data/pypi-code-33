""" Implementations of various geometry data structures. """

from math import sqrt, atan2

class Point():
    """ Point in 2D space. """

    def __init__(self, x=0, y=0):
        """ Class constructor. """
        if isinstance(x, Point):
            self.x, self.y = x.x, x.y
        elif isinstance(x, (type([]), type(()))): # check if x is a list or a tuple
            self.x, self.y = x
        elif isinstance(x, complex):
            self.x, self.y = x.real, x.imag
        else:
            self.x, self.y = x, y

    def __set(self, other):
        """ Update self instance with another value. """
        self.__dict__.update(other.__dict__)
        return self

    def __iter__(self):
        return iter((self.x, self.y))
    def __getitem__(self, idx):
        return tuple(self)[idx]

    def __eq__(self, other):
        if isinstance(other, Point):
            return tuple(self) == tuple(other)
        return self == Point(other)
    def __ne__(self, other):
        return not self == other
    def __lt__(self, other):
        return tuple(self) < tuple(other)
    def __gt__(self, other):
        return tuple(self) > tuple(other)
    def __le__(self, other):
        return tuple(self) <= tuple(other)
    def __ge__(self, other):
        return tuple(self) >= tuple(other)

    def cross(self, other):
        """ The cross product of two Points. """
        return self.x * other.y - self.y * other.x
    def __pow__(self, other):
        """ Another way to use cross. """
        return self.cross(other)

    def dot(self, other):
        """ The dot product of two Points. """
        return self.x * other.x + self.y * other.y
    def __mul__(self, other):
        """ When sent a Point, will calculate the dot product, when sent a
            escalar, will multiply the point coordinates by that scalar """
        if isinstance(other, Point):
            return self.dot(other)
        return Point(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self * other

    def __add__(self, other):
        """ Adds two Points. """
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        return self + Point(other)
    def __radd__(self, other):
        return self + other
    def __sub__(self, other):
        """ Subtracts two Points. """
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        return self - Point(other)
    def __rsub__(self, other):
        return Point(other) - self
    def __truediv__(self, other):
        """ Divides a point by a scalar. """
        return Point(self.x / other, self.y / other)
    def __floordiv__(self, other):
        """ Integer division. """
        return Point(self.x // other, self.y // other)
    def __mod__(self, other):
        """ Takes mod. """
        return Point(self.x % other, self.y % other)

    def __iadd__(self, other):
        return self.__set(self + other)
    def __isub__(self, other):
        return self.__set(self - other)
    def __itruediv__(self, other):
        return self.__set(self / other)
    def __ifloordiv__(self, other):
        return self.__set(self // other)
    def __imod__(self, other):
        return self.__set(self % other)
    def __imul__(self, other):
        return self.__set(self * other)

    def __abs__(self):
        """ Distance to (0, 0). """
        return sqrt(self.x ** 2 + self.y ** 2)
    def len(self):
        """ Distance to (0, 0). """
        return abs(self)

    def __complex__(self):
        """ Convert to complex. """
        return complex(self.x, self.y)

    def __pos__(self):
        return Point(self)
    def __neg__(self):
        return Point(-self.x, -self.y) # pylint: disable=invalid-unary-operand-type
    def __trunc__(self):
        """ Truncate to int. """
        return Point(int(self.x), int(self.y))

    def normalized(self):
        """ Normalized vector from origin to this Point. """
        length = abs(self)
        return Point() if length == 0 else self / abs(self)
    def normalize(self):
        """ Normalizes this Point. """
        return self.__set(self.normalized())

    def ang(self):
        """ Return math.atan2(x, y). """
        return atan2(self.x, self.y)

    def __str__(self):
        """ String representation of a Point. """
        return str(tuple(self))

class Segment():
    """ Segment in 2D space. """

    def __init__(self, a, b):
        self.a, self.b = a, b

    def __abs__(self):
        return abs(self.b - self.a)
    def len(self):
        """ Size of segment. """
        return abs(self)

    def __eq__(self, other):
        return (self.a, self.b) == (other.a, other.b) or (self.a, self.b) == (other.b, other.a)

    def __pin(self):
        """ Returns Point b - a. """
        return self.b - self.a

    def __contains__(self, other):
        """ Check if a Point belongs to this segment. """
        if (other - self.a) ** self.__pin() == 0 and abs(2 * other - self.a - self.b) <= self.len():
            return True
        return False

    def intersection(self, other):
        """ Intersection of segment with something else.
            Returns 'None' if there is no intersection. """
        if isinstance(other, Point) and other in self:
            return other
        if isinstance(other, Segment):
            if (other.a - self.a) ** self.__pin() == 0 and (other.b - self.a) ** self.__pin() == 0:
                p, q = sorted([other.a, other.b, self.a, self.b])[1: 3]
                if p in self and p in other:
                    return Segment(p, q)
            else:
                e, f = (self.b - self.a), (other.b - other.a)
                p = Point(-e.y, e.x)
                h = ((self.a - other.a) * p) / (f * p)
                if 0 < h <= 1:
                    return other.a + f * h
        return None
