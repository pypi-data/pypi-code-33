
# Copyright (C) 2018-19 Frank Sauerburger

"""
The python package pyveu (Value Error Unit) handles real-life experimental
data which includes uncertainties and physical units. The packages implements
arithmetic operations and many mathematical functions for physical quantities.
Gaussian error propagation is used to calculate the uncertainty of derived
quantities.

The package is built with the day-to-day requirements of people working a
laboratory kept in mind. The package offers an imperative programming style,
which means that the operations are evaluated when they are typed
interactively in python, giving researcher the freedom and flexibility they
need.

"""

from __future__ import division  # Compatibility with 2.7
from builtins import int, round   # Compatibility with 2.7

import collections
import numpy as np
import re
import math
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR

# The content of the file might be move to other module within the same
# package.

def join_or_none(a, b):
    """
    Joins the two strings. If one argument is None, the other argument is
    returned. If both arguments are None, None is returned.
    """
    if a is None and b is None:
        return None
    elif a is None:
        return b
    elif b is None:
        return a
    else:
        return a + b

def _round(value, precision=0):
    """
    Rounds the value to the given precision. The optional parameter precision
    is the number of decimal digits after rounding. The value is rounded to
    the nearest number with the given precision. In case of a tie, the method
    rounds away from zero. The precision can be negative.

    The method returns an integer for negative precision.
    """
    scale = Decimal(10)**precision
    floored = (Decimal(value) * scale).to_integral(ROUND_HALF_UP) / scale

    if precision <= 0:
        return int(floored)
    else:
        return float(floored)

def _floor(value, precision=0):
    """
    Rounds the value down to the given precision. The optional parameter precision
    is the number of decimal digits after rounding. The value is always
    rounding down. This means positive values are rounded towards zero,
    negative values are rounded away from zero. The precision can be negative.

    The method returns an integer for negative precision.
    """
    scale = Decimal(10)**precision
    floored = (Decimal(value) * scale).to_integral(ROUND_FLOOR) / scale

    if precision <= 0:
        return int(floored)
    else:
        return float(floored)

class Named(object):
    """
    The class Named defines the base class for all classes in this package,
    which have a label, a mathematical symbol and optionally and alternative
    latex representation.

    The label should be used to describe an object with a verbose, human
    readable string. In case of a physical quantity, the label can be
    'Current', 'Voltage of the photo diode' or similar strings. The label can
    be retrieved with the label() method.

    The symbol should be used to decorate object with a mathematical symbol.
    If the named object stores time information, an intuitively
    understandable symbol is `t`.  The symbol is used when the named object is
    printed on the console. The symbol should not use latex syntax.

    The latex property stores an alternative representation of the symbol with
    latex support. Dollar signs should not be included in the string. For
    example, the latex symbol of the dielectric constant in matter is commonly
    set to `\\epsilon_r`.

    The base class Named does not define methods to modify the properties.
    This means, unless a derived class uses the ModifiableNamed mix-in, the
    name properties are read-only.
    """

    def __init__(self, label, symbol, latex):
        """
        Creates a new named object. This method is intended to be called by
        the constructors of derived classes.
        """
        self._label = label
        self._symbol = symbol
        self._latex = latex

    def symbol(self):
        """
        Returns the non-latex symbol. The symbol property is read-only.
        """
        return self._symbol

    def latex(self):
        """
        Returns the latex symbol. The latex symbol property is read-only.
        """
        return self._latex

    def lors(self):
        """
        Returns the latex symbol if it is not None. Otherwise the symbol is returned.
        This method is read-only. The name of the method stands for
        latex-or-symbol.
        """
        return self.symbol() if self.latex() is None else self.latex()

    def label(self):
        """
        Returns the verbose label of the named object. The label is read-only.
        """
        return self._label

class ModifiableNamedMixin(object):
    """
    Overrides symbol(), latex() and label(). The new methods support
    modification of these properties, by passing a value to the method.
    """

    def label(self, *args):
        """
        Set or get the label. If the arguments are omitted, the method returns
        the current label. If an argument is given, the argument is used as
        the new label.
        """
        if len(args) == 0:
            return self._label
        elif len(args) == 1:
            self._label = args[0]
        else:
            raise TypeError("label() takes 0 or 1 arguments (%d given)" \
                            % len(args))


    def symbol(self, *args):
        """
        Set or get the symbol. If the arguments are omitted, the method returns
        the current symbol. If an argument is given, the argument is used as
        the new symbol.
        """
        if len(args) == 0:
            return self._symbol
        elif len(args) == 1:
            self._symbol = args[0]
        else:
            raise TypeError("symbol() takes 0 or 1 arguments (%d given)" \
                            % len(args))

    def latex(self, *args):
        """
        Set or get the latex symbol. If the arguments are omitted, the method
        returns the current latex symbol. If an argument is given, the
        argument is used as the new latex symbol.
        """
        if len(args) == 0:
            return self._latex
        elif len(args) == 1:
            self._latex = args[0]
        else:
            raise TypeError("latex() takes 0 or 1 arguments (%d given)" \
                            % len(args))

class SystemAffiliatedMixin:
    """
    The SystemAffiliatedMixin class can be used as a mix-in to indicate that a
    class is affiliated with a particular unit system. The unit system can be
    set in the constructor. Later modifications of the unit system are not
    possible. The current unit system object can be retrieved via the
    unit_system() method.
    """
    def __init__(self, unit_system):
        """
        Constructor of a SystemAffiliated mix-in. This method should be called
        in constructors of other classes which use the mix-in. The first
        argument is expected to be a unit system object.
        """
        self._unit_system = unit_system 

    def unit_system(self):
        """
        Returns the unit system to which the object is affiliated. This method
        is read-only.
        """
        return self._unit_system

class _Arithmetic:
    """
    The arithmetic class is the base class of arithmetic operations which are
    used to record the history how anonymous units and prefixes were
    constructed. Each arithmetic operation performed with prefixes or units
    are reflected in object dependencies of sub-classes. The main purpose of
    this class an sub-classes is to store all the operands used in the
    arithmetic operations.
    """
    pass

class _Product(_Arithmetic):
    """
    The product class represents a multiplication of two or more factors. The
    main purpose of this class is to store the factors.
    """

    def __init__(self, *factors):
        """
        Create a new product object. All argument of the constructor are
        treated as factor of the product. If there are less than two factors,
        an Exception is raised.
        """
        if len(factors) < 2:
            raise TypeError("_Product expects at least do factors.")

        self.factors = list(factors)
   
    def str(self, latex=False):
        """
        Create a string representation by calling str() on all factors. The
        method adds parenthesis when needed. Factors are joined by an
        asterisk. If the optional parameter latex is True, then a latex version
        of the string is constructed.
        """
        if len(self.factors) < 2:
            raise ValueError("_Product expects at least two factors.")

        str_factors = []
        for factor in self.factors:
            if isinstance(factor, _Arithmetic):
                str_factors.append(factor.str(latex))
            elif isinstance(factor, Unit) and latex:
                str_factors.append(factor.lors())
            elif isinstance(factor, Unit) and not latex:
                str_factors.append(factor.symbol())
            elif isinstance(factor, Prefix):
                str_factors.append("%g" % factor.factor())
            elif isinstance(factor, (int, float)):
                str_factors.append("%g" % factor)
            else:
                str_factors.append(str(factor))

        if latex:
            return " ".join(str_factors)
        else:
            return " * ".join(str_factors)

    def __str__(self):
        """
        Calls _Product.str().
        """
        return self.str()


    def __repr__(self):
        """
        Create a string representation by calling str() on all factors. The
        method adds parenthesis around all sub-arithmetical objects.
        """
        if len(self.factors) < 2:
            raise ValueError("_Product expects at least do factors.")

        str_factors = ["(%s)" % repr(f) if isinstance(f, _Arithmetic) \
                       else repr(f) for f in self.factors]
        return " * ".join(str_factors)

class _Fraction(_Arithmetic):
    """
    The fraction class represents a division of two objects. The
    main purpose of this class is to store the numerator an denominator.
    """

    def __init__(self, numerator, denominator):
        """
        Create a new fraction object. The constructor expects and stores an
        numerator and denominator object.
        """
        self.numerator = numerator
        self.denominator = denominator
   
    def str(self, latex=False):
        """
        Create a string representation by calling str() on the numerator and
        denominator. The method adds parenthesis when needed. Factors are
        joined by an asterisk. If the optional parameter latex is True, then a
        latex version of the string is constructed.
        """
        if isinstance(self.numerator, _Arithmetic):
            str_numerator = self.numerator.str(latex)
        elif isinstance(self.numerator, Unit) and latex:
            str_numerator = self.numerator.lors()
        elif isinstance(self.numerator, Unit) and not latex:
            str_numerator = self.numerator.symbol()
        elif isinstance(self.numerator, Prefix):
            str_numerator = "%g" % factor.factor()
        elif isinstance(self.numerator, (int, float)):
            str_numerator = "%g" % self.numerator
        else:
            str_numerator = str(self.numerator)

        if isinstance(self.denominator, _Power):
            str_denominator = self.denominator.str(latex)
        elif isinstance(self.denominator, _Arithmetic) and latex:
            str_denominator = self.denominator.str(latex)
        elif isinstance(self.denominator, _Arithmetic) and not latex:
            str_denominator = "(%s)" % self.denominator.str(latex)
        elif isinstance(self.denominator, Unit) and latex:
            str_denominator = self.denominator.lors()
        elif isinstance(self.denominator, Unit) and not latex:
            str_denominator = self.denominator.symbol()
        elif isinstance(self.denominator, Prefix):
            str_denominator = "%g" % factor.factor()
        elif isinstance(self.denominator, (int, float)):
            str_denominator = "%g" % self.denominator
        else:
            str_denominator = str(self.denominator)

        if latex:
            return r"\frac{%s}{%s}" % (str_numerator, str_denominator)
        else:
            return "%s / %s" % (str_numerator, str_denominator)

    def __str__(self):
        """
        Calls _Fraction.str().
        """
        return self.str()
   
    def __repr__(self):
        """
        Create a string representation by calling str() on the numerator and
        denominator. The method adds parenthesis around all sub-arithmetical
        objects.
        """
        def escape(item):
            if isinstance(item, _Arithmetic):
                return "(%s)" % repr(item)
            else:
                return repr(item)

        return "%s / %s" % (escape(self.numerator), escape(self.denominator))

class _Power(_Arithmetic):
    """
    The power class represents a power of two objects. The
    main purpose of this class is to store the base and the exponent.
    """

    def __init__(self, base, exponent):
        """
        Create a new power object. The constructor expects and stores a base
        and exponent object.
        """
        self.base = base
        self.exponent = exponent
   
    def str(self, latex=False):
        """
        Create a string representation by calling str() on the base and
        exponent. The method adds parenthesis when needed. If the optional
        parameter latex is True, then a latex version of the string is
        constructed.
        """
        if isinstance(self.base, _Arithmetic) and latex:
            base = r"\left(%s\right)" % self.base.str(latex)
        elif isinstance(self.base, _Arithmetic) and not latex:
            base = "(%s)" % self.base.str(latex)
        elif isinstance(self.base, Unit) and latex:
            base = self.base.lors()
        elif isinstance(self.base, Unit) and not latex:
            base = self.base.symbol()
        elif isinstance(self.base, (int, float)):
            base = "%g" % self.base
        else:
            base = str(self.base)

        if isinstance(self.exponent, _Arithmetic) and latex:
            exponent = self.exponent.str(latex)
        elif isinstance(self.exponent, (_Fraction, _Product)) and not latex:
            exponent = "(%s)" % self.exponent.str(latex)
        elif isinstance(self.exponent, _Arithmetic) and not latex:
            exponent = self.exponent.str(latex)
        elif isinstance(self.exponent, Unit) and latex:
            exponent = self.exponent.lors()
        elif isinstance(self.exponent, Unit) and not latex:
            exponent = self.exponent.symbol()
        elif isinstance(self.exponent, (int, float)):
            exponent = "%g" % self.exponent
        else:
            exponent = str(self.exponent)

        if latex:
            return "%s^{%s}" % (base, exponent)
        else:
            return "%s^%s" % (base, exponent)
   

    def __str__(self):
        """
        Calls _Power.str()
        """
        return self.str()

    def __repr__(self):
        """
        Create a string representation by calling repr() on the base and
        exponent. The method adds parenthesis around sub-arithmetical objects.
        """
        def escape(item):
            if isinstance(item, _Arithmetic):
                return "(%s)" % repr(item)
            else:
                return repr(item)

        return "%s^%s" % (escape(self.base), escape(self.exponent))

class Prefix(Named, SystemAffiliatedMixin):
    """
    The Prefix class represents a string with which units can be prepended in
    order to scale them. A popular example are the SI prefixes such as Kilo,
    Mega or Giga. A prefix can be created via a unit system. The unit system
    adds all prefixes to its internal registry. Registered prefixes are
    considered when parsing unit strings.

    The prefix class inherits the label, symbol and latex property of the
    Named class. Furthermore, the class inherits the properties of the
    SystemAffiliated class and is therefore tied to a particular unit system.

    In addition to the inherited properties, this class stores a factor which
    is used to scale a unit. For example, the factor of the prefix Kilo is
    1000.

    Multiplications and divisions are overloaded for units. Multiplications and
    divisions of a prefix and a number return a number in most of the cases.
    The only exception is the case when prefix is multiplied by a number from
    the left, e.g., 10 * kilo. In that case, the result is an anonymous
    prefix. Its history is a product with the two factors 10 and kilo.
    These derived prefixes are not automatically added to the registry. If you
    want to add an anonymous prefix to the registry, use the register_prefix()
    method of the unit system.
    """
    
    def __init__(self, factor, label, symbol, latex, unit_system):
        """
        This method is for internal usage only.

        Creates a new Prefix. Prefixes should be created via a unit system.
        """
        Named.__init__(self, label, symbol, latex)
        SystemAffiliatedMixin.__init__(self, unit_system)

        self._factor = factor
        self._history = None

    def factor(self):
        """
        Returns the factor of the prefix. This method is read-only.
        """
        return self._factor

    def __repr__(self):
        """
        Returns a string which can be used to recreate the object. The string
        has the following pattern:
            
            <Prefix <label>: <symbol> = <factor>>

        If the label of symbol is None, they are excluded from the
        representation.
        """
        if self._label is None and self._symbol is None:
            id = ": "
        elif self._label is None:
            id = ": %s = " % self._symbol
        elif self._symbol is None:
            id = " %s: " % self._label
        else:
            id = " %s: %s = " % (self._label, self._symbol)

        return "<Prefix%s%g>" % (id, self._factor)

    def __mul__(self, other):
        """
        Multiplies the factor with the given operand. The operand must be
        integer, float or Prefix, otherwise NotImplemented is returned. This
        allows Unit and Quantity to implement custom behavior.

        The method returns a simple number (float or int).
        """
        if not isinstance(other, (int, float, Prefix)):
            return NotImplemented

        if isinstance(other, SystemAffiliatedMixin):
            if self.unit_system() is not other.unit_system():
                raise DifferentUnitSystem()

        if isinstance(other, Prefix):
            other = other.factor()

        # Return simple number
        return self.factor() * other
        

    def __rmul__(self, other):
        """
        Multiplies the factor with the given operand. The operand must be
        integer, float or Prefix, otherwise NotImplemented is returned. This
        allows Unit and Quantity to implement custom behavior.

        The method returns a simple number (float or int). The only exception
        is when a prefix is multiplied by a number form the left, e.g.,
        10 * kilo. In that case, the method returns a new object. The prefix
        on which this method is called is not modified. The new prefix is
        anonymous and not registered. To register it, use the
        register_prefix() method of the unit system. The new Prefix's history
        is a Product of the scalar and the original prefix.
        """
        if not isinstance(other, (int, float, Prefix)):
            return NotImplemented

        if isinstance(other, SystemAffiliatedMixin):
            if self.unit_system() is not other.unit_system():
                raise DifferentUnitSystem()

        if isinstance(other, Prefix):
            # Return simple number
            return self.factor() * other.factor()

        # Return a new, unnamed prefix
        new_prefix =  Prefix(self.factor() * other, None, None, None,
                             self.unit_system())

        # Calculate new history
        if self._history is None:
            if self.symbol() is None:
                raise Exception("History of the other unnamed prefix shouldn't "
                                "be None. How was the unit created? "
                                "This is probably a bug.")
            new_prefix._history = _Product(other, self)
        else:
            new_prefix._history = _Product(other, *self._history.factors)

        return new_prefix

    def __truediv__(self, other):
        """
        Divides the factor by the given operand. The operand must be
        integer, float or Prefix, otherwise NotImplemented is returned. This
        allows Unit and Quantity to implement custom behavior.

        The method returns a simple number (int, float).
        """
        if not isinstance(other, (int, float, Prefix)):
            return NotImplemented

        if isinstance(other, SystemAffiliatedMixin):
            if self.unit_system() is not other.unit_system():
                raise DifferentUnitSystem()

        if isinstance(other, Prefix):
            other = other.factor()

        # Create new anonymous Prefix
        return self.factor() / other

    def __rtruediv__(self, other):
        """
        See __truediv__(). Similar, but with reversed roles.
        """
        if not isinstance(other, (int, float, Prefix)):
            return NotImplemented

        if isinstance(other, SystemAffiliatedMixin):
            if self.unit_system() is not other.unit_system():
                raise DifferentUnitSystem()

        if isinstance(other, Prefix):
            other = other.factor()

        # Create new anonymous Prefix
        return other / self.factor()

    def __div__(self, other):
        """
        Compatibility with Python 2.7. 

        The standard division (/) in Python 2.7 calls this method. Dividing a
        Prefix by an integer should not floor the factor.
        """
        return self.__truediv__(other)

    def __rdiv__(self, other):
        """
        Compatibility with Python 2.7. 

        The standard division (/) in Python 2.7 calls this method. Dividing a
        Prefix by an integer should not floor the factor.
        """
        return self.__rtruediv__(other)

    def history_str(self, latex=False):
        """
        Returns a string representation of the history. If the optional
        parameter latex=True, a latex version of the string is created. If the
        history is None, returns None. This method completely includes scalar
        factors in the history.
        """
        if self._history is None:
            return None
        else:
            return self._history.str(latex=latex)

class Unit(Named, SystemAffiliatedMixin):
    """
    The unit class represents physical units, such as Ampere or Newton. A unit
    is created by a unit system. A unit is permanently tied to the creating
    unit system. It is not necessary to create units with all possible
    prefixes. Prefixes are automatically handled once they are registered with
    a unit system.

    A unit inherits all the properties from Named and SystemAffiliated.
    Additionally, a factor and a unit vector is stored.  The unit vector
    stores the exponents of the base units. Assume a unit system with three
    base units A, B and C. A unit with a unit vector of [0, 2, 1] corresponds to
    A^0 * B^2 * C^1. The factor can be used to generated arbitrarily scaled
    derived units. For example, if you set the factor to 60, the unit
    represent minutes, if it has the same unit vector as seconds. Please note
    that it is not necessary to register units with prefixes. Prefixes are
    handles by the unit system.

    Multiplications, divisions and powers are overloaded for units. These
    operations create a new unit object. The resulting objects are anonymous,
    i.e. their label and symbol properties are None. Furthermore, these
    derived units are not automatically added to the registry. If you want to
    add a anonymous unit to the registry, use the register_unit() method of
    the unit system.

    The properties of a unit can not be changed.
    """
    def __init__(self, factor, unit_vector, label, symbol, latex,
                 unit_system):
        """
        For internal usage only.

        Creates a new Unit. Units should be created via a unit system.
        """
        Named.__init__(self, label, symbol, latex)
        SystemAffiliatedMixin.__init__(self, unit_system)

        # Mathematical operations consider only the factor and the
        # unit_vector.
        self._factor = factor
        self._unit_vector = np.array(unit_vector)  # copy external vector

        # The history of a unit is not used to perform actual calculations.
        # The history is maintained inorder to be able to print the unit in a
        # user friendly way.
        self._history = None

    @staticmethod
    def create_with_history(factor, unit_vector, unit_system):
        """
        For internal usage only.

        Alternative method to create a unit. Instead of assembling a new Unit
        from scratch, it is created by multiplying, dividing and
        exponentiating base units. The return value is an anonymous unit with
        a minimal history of base units.

        If the final unit is dimensionless (i.e. unit_vector = [0, 0, ...]),
        the factor is multiplied by the first base unit to the 0-th power.
        """
        # Create initial history
        numerator_factors= []
        denominator_factors= []
        if factor != 1:
            numerator_factors.append(factor)

        for unit, exp in zip(unit_system._reg_base, unit_vector):
            if exp == 1:
                numerator_factors.append(unit)
            elif exp > 0:
                numerator_factors.append(unit**exp)
            elif exp == -1:
                denominator_factors.append(unit)
            elif exp < 0:
                denominator_factors.append(unit**(-exp))

        if len(numerator_factors):
            unit = numerator_factors[0]
            for factor in numerator_factors[1:]:
                unit *= factor
        else:
            unit = 1

        if len(denominator_factors):
            denominator = denominator_factors[0]
            for factor in denominator_factors[1:]:
                denominator *= factor
            unit /= denominator

        if isinstance(unit, (int, float)):
            unit *= unit_system._reg_base[0]**0

        return unit

    def __pow__(self, power):
        """
        Returns the power of the unit. The power of the unit is calculated by
        exponentiating the factor and multiplying the unit vector with the
        given exponent. The exponent argument must be an integer or float.
        
        The method returns a new object, the object on which this method is
        called remains unchanged. The returned object is anonymous and not
        registered.
        """
        ######################################################
        # Type checks
        if not isinstance(power, (int, float)):
            return NotImplemented

        ######################################################
        # Determine history
        if self.symbol() is None:
            history = _Power(self._history, power)
        else:
            history = _Power(self, power)


        ######################################################
        # Determine factor
        factor = self.factor()**power
        unit_vector = self.unit_vector() * power

        ######################################################
        # Assemble unit
        unit = Unit(factor, unit_vector, None, None, None, self.unit_system())
        unit._history = history

        return unit
    
    def __mul__(self, other, reverse=False):
        """
        Returns the product of the unit with the other operand. If the other
        operand is an integer, float or Prefix, only the factor is multiplied
        by the given number (or factor of the prefix). The unit vector is not
        affected. If the other operand is a unit object, the product of the
        two factors is calculated and the unit vectors are added.

        If the other operand is neither integer, float, Prefix nor unit object,
        NotImplemented is returned. This makes it possible to implement custom
        behavior in the Quantity class.

        The method returns a new object, the object on which this method is
        called remains unchanged. The returned object is anonymous and not
        registered.

        if reverse is True, the multiplication order is reversed.
        """

        ######################################################
        # Type checks
        if not isinstance(other, (int, float, Prefix, Unit)):
            return NotImplemented

        if isinstance(other, SystemAffiliatedMixin):
            if other.unit_system() is not self.unit_system():
                raise DifferentUnitSystem()

        ######################################################
        # Determine history

        # Recording of the history has been changed, see #9 and #17.
            
        factors = []
    
        #######################
        # Self history
        #  1. Named unit: If a named unit is encountered, use the unit
        #     directly and do not copy any of its history.
        #  2. Unnamed unit without history: error
        #  3. History is _Product: If a participant is a product, extract the
        #     factors and assemble joint product.
        #  4. History is _Arithmetic: If an other _Arithmetic is encountered,
        #     it should be a factor of the resulting product.

        if self.symbol() is not None:
            factors.append(self)  # Named
        elif self._history is None:
            # History is none
            raise Exception("History of this unnamed unit shouldn't be None. "
                            "How was the unit created? "
                            "This is probably a bug.")
        elif isinstance(self._history, _Product):
            factors.extend(self._history.factors)  # Product
        elif isinstance(self._history, _Arithmetic):
            factors.append(self._history)  # Arithmetic
        else:
            raise Exception("This is a bug. This unit has an unexpected "
                            "history. How was it created?")

        if reverse:
            factors_self = factors
            factors = []

        #######################
        # Other history
        #  1. Named unit/prefix: If a named unit/prefix is encountered, use
        #     the unit/prefix directly and do not copy any of its history.
        #  2. Unnamed unit/prefix without history: error
        #  3. History is _Product: If a participant is a product, extract the
        #     factors and assemble joint product.
        #  4. History is _Arithmetic: If an other _Arithmetic is encountered,
        #     it should be a factor of the resulting product.
        #  5. If other is neither Unit nor Prefix, use as factor.
        if isinstance(other, (Unit, Prefix)):
            if other.symbol() is not None:
                factors.append(other)  # Named
            elif other._history is None:
                # History is none
                raise Exception("History of this unnamed unit/prefix shouldn't be None. "
                                "How was the unit created? "
                                "This is probably a bug.")
            elif isinstance(other._history, _Product):
                factors.extend(other._history.factors)  # Product
            elif isinstance(other._history, _Arithmetic):
                factors.append(other._history)  # Arithmetic
        else:
            # Other is number
            factors.append(other)

        if reverse:
            factors.extend(factors_self)

        #######################
        # Build history object
        history = _Product(*factors)
        
        ######################################################
        # Determine unit vector and factor
        unit_vector = self.unit_vector()
        if isinstance(other, Unit):
            unit_vector += other.unit_vector()
            other = other.factor()

        if isinstance(other, Prefix):
            other = other.factor()
        factor = self.factor() * other

        ######################################################
        # Assemble new unit
        result = Unit(factor, unit_vector, None, None, None, self.unit_system())
        result._history = history
        
        return result


    def __rmul__(self, other):
        """
        See __mul__(). This operation is equivalent to __mul__ since
        multiplication is commutative.
        """
        return self.__mul__(other, reverse=True)

    def __truediv__(self, other, reverse=False):
        """
        Returns the division of the unit with the other operand. If the other
        operand is an integer, float or Prefix, only the factor is divided
        by the given number (or factor of the prefix). The unit vector is not
        affected. If the other operand is a unit object, the fraction of the
        two factors is calculated and the unit vectors are subtracted.

        If the other operand is neither integer, float, Prefix nor unit object,
        NotImplemented is returned. This makes it possible to implement custom
        behavior in the Quantity class.

        The method returns a new object, the object on which this method is
        called remains unchanged. The returned object is anonymous and not
        registered.

        If reverse is True, exchanges the order of the division.
        """
        ######################################################
        # Type checks
        if not isinstance(other, (int, float, Prefix, Unit)):
            return NotImplemented

        if isinstance(other, SystemAffiliatedMixin):
            if other.unit_system() is not self.unit_system():
                raise DifferentUnitSystem()

        ######################################################
        # Determine history

        # Recording of the history has been changed, see #9 and #17.
    
        numerator = None
        denominator = None
    
        #######################
        # Self history
        #  1. Named unit: If a named unit is encountered, use the unit
        #     directly and do not copy any of its history.
        #  2. Unnamed unit without history: error
        #  3. History is _Arithmetic: If an other _Arithmetic is encountered,
        #     it should be a numerator of the resulting fraction.
        if self.symbol() is not None:
            numerator = self  # Named
        elif self._history is None:
            # History is none
            raise Exception("History of this unnamed unit shouldn't be None. "
                            "How was the unit created? "
                            "This is probably a bug.")
        elif isinstance(self._history, _Arithmetic):
            numerator = self._history  # Arithmetic
        else:
            raise Exception("This is a bug. This unit has an unexpected "
                           "history. How was it created?")

        #######################
        # Other history
        #  1. Named unit/prefix: If a named unit/prefix is encountered, use
        #     the unit/prefix directly and do not copy any of its history.
        #  2. Unnamed unit/prefix without history: error
        #  3. History is _Product: If a participant is a product, extract the
        #     factors and assemble joint product.
        #  4. History is _Arithmetic: If an other _Arithmetic is encountered,
        #     it should be a factor of the resulting product.
        #  5. If other is neither Unit nor Prefix, use as factor.
        if isinstance(other, (Unit, Prefix)):
            if other.symbol() is not None:
                denominator = other  # Named
            elif other._history is None:
                # History is none
                raise Exception("History of the other unnamed unit shouldn't "
                                "be None. How was the unit created? "
                                "This is probably a bug.")
            elif isinstance(other._history, _Arithmetic):
                denominator = other._history  # Arithmetic
            else:
                raise Exception("This is a bug. The other unit has an unexpected "
                                "history. How was it created?")
        else:
            # Other is number
            denominator = other

        #######################
        # Build history object
        if reverse:
            history = _Fraction(denominator, numerator)
        else:
            history = _Fraction(numerator, denominator)
      
        ######################################################
        # Determine unit vector and factor
        unit_vector = self.unit_vector()
        if isinstance(other, Unit):
            unit_vector -= other.unit_vector()
            other = other.factor()

        if reverse:
            unit_vector *= -1

        if isinstance(other, Prefix):
             other = other.factor()
        
        if reverse:  # Might avoid rounding errors
            factor = other / self.factor()
        else:
            factor = self.factor() / other

        ######################################################
        # Assemble unit vector
        unit = Unit(factor, unit_vector, None, None, None, self.unit_system())
        unit._history = history

        return unit

    def __rtruediv__(self, other):
        """
        See __div__(). Similar, but with reversed roles.
        """
        return self.__truediv__(other, reverse=True)

    def __div__(self, other):
        """
        Compatibility with Python 2.7. 

        The standard division (/) in Python 2.7 calls this method. Dividing a
        Unit by an integer should not floor the factor.
        """
        return self.__truediv__(other)

    def __rdiv__(self, other):
        """
        Compatibility with Python 2.7. 

        The standard division (/) in Python 2.7 calls this method. Dividing a
        Unit by an integer should not floor the factor.
        """
        return self.__rtruediv__(other)

    def unit_vector(self):
        """
        Returns the unit vector of the unit. The stores the exponents of the
        base units. The unit (neglecting the factor of the unit) is the
        product of all base units raised to the powers stored in the unit
        vector. The i-th value in the unit vector specifies the power of the
        i-th base unit.
        
        Unit vectors are stored as numpy arrays. This method returns a copy of
        the numpy array.

        This method provides read-only access.
        """
        return np.array(self._unit_vector)

    def dimensionless(self):
        """
        Consults the unit system to see, whether this unit is dimensionless,
        and turns the outcome. If this is true, the unit can be used in
        mathematical functions such as Sine or the exponential function. 
        """
        return self.unit_system().dimensionless(self)

    def factor(self):
        """
        Returns the factor of the units. This method provides read-only access
        to the factor.
        """
        return self._factor

    def __repr__(self):
        """
        Returns a string which shows the label and the symbol of the unit and
        its relation to base units. The returned string has the following pattern:

            <Unit <label>: 1 <symbol> = <factor> <A>^<a> <B>^<b> ... >

        where a and b are non-zero elements of the unit vector and A and B are base
        units with non-zero powers. If a symbol or a label is None, it is
        removed from the string representation.
        """
        pre_colon = ["Unit"]
        post_colon = []

        if self._label is not None:
            pre_colon.append(self._label)

        if self._symbol is not None:
            post_colon.append("1")
            post_colon.append(self._symbol)
            post_colon.append("=")

        post_colon.append("%g" % self._factor)

        base_repr = self._unit_system.base_representation(self._unit_vector)
        post_colon.append(base_repr)

        return "<%s: %s>" % (" ".join(pre_colon), " ".join(post_colon))

    def history_str(self, latex=False):
        """
        Returns a string representation of the history. If the optional
        parameter latex=True, a latex version of the string is created. If the
        history is None, returns None. This method completely ignores the
        factor of the unit.
        """
        if self._history is None:
            return None
        else:
            return self._history.str(latex=latex)

    def base_representation(self, latex=False, suppress_factor=False):
        """
        Returns the unit using only base units. If the optional argument latex
        is True, this method returns a latex version. By default the returned
        string includes the factor of the unit. If suppress_factor is True,
        the returned string excludes the factor.
        """
        base_repr = self.unit_system().base_representation(self.unit_vector(),
                                                       latex)

        if suppress_factor:
            return base_repr
        else:
            return "%g %s" % (self.factor(), base_repr)

    def str(self, latex=False):
        """
        If the unit is unnamed returns the factor and the history of the unit.
        If the unit is named, returns the symbol. If the optional parameter
        latex=True, latex version of the string is created.
        """
        if self.symbol() is None:
            return self.history_str(latex)
        else:
            if latex:
                return self.lors()
            else:
                return self.symbol()

    def __str__(self):
        """
        Calls Unit.str().
        """
        return self.str()

class UnitSystem:
    """
    This class represents a unit system. This means it holds the definition of
    all base units. The set of base units spans a vector space (multiplication
    of base units is the vector space addition). All derived units are vectors
    in the vector space, this means they can be represented as a linear
    combination of the base vectors.
    
    The class also functions as a factory for units belonging
    to this unit system. The unit system keeps a registry of all units created
    within this system. The registry can be used to parse unit strings.
    Similarly, the unit system creates and registers prefixes which can be
    prepended to all units.

    A unit is considered dimensionless, if it is a linear combination of
    dimensionless base units. This means there can not be a linear combination of
    base vectors considered as dimensionless, which is not pure linear
    combination of dimensionless vector.
    """

    def __init__(self, name, n_base, n_dimensionless=0):
        """
        Creates a new unit system. The first argument specifies the number of
        base units. The second argument defines how many of them are
        considered to be dimensionless (n_base >= n_dimensionless). By
        convention the base units are numbered 0, 1, ..., n_base - 1. The last
        n_dimensionless base units are dimensionless.

        A freshly created unit system is agnostic of its base units names. To
        add names (labels, symbols and latex symbols) use the
        create_base_unit() method. Please note that this merely generated the
        unit objects and defines the names of the base units. This does not
        register the base units (unless register=True in create_base_unit()).

        Until all base units have been created, the placeholder [base#i] is
        use in string representations for the i-th base unit.
        """
        self._name = name
        self._n_base = n_base
        self._n_dimensionless = n_dimensionless

        self._reg_base = [None] * n_base

        self._dimensionless_mask = np.zeros(n_base)
        self._dimensionless_mask[-n_dimensionless:] = 1

        self._reg_prefixes_all = []
        self._reg_prefixes_latex = {}
        self._reg_prefixes_label = {}
        self._reg_prefixes_symbol = {}

        self._reg_units_all = []
        self._reg_units_latex = {}
        self._reg_units_label = {}
        self._reg_units_symbol = {}

    def create_base_unit(self, index, label, symbol, latex=None,
                         register=False):
        """
        Creates a unit for the base unit identified with the given index. The
        created unit is returned. The created unit is not registered unless
        the argument 'register' is set to True.

        Please note that base units can not be scaled by a factor. Unlike
        create_unit, this method does not register the unit. Therefore,
        unregistered base units do not take part in the unit string parsing.

        This mechanism is useful if a base unit has a prefix, such as
        kilogram. The base class is kilogram. However, in order that prefixes
        work as expected (i.e. not create a double prefix Mkg, Mega-kilogram),
        one can register a non-base unit gram. Only gram is be considered
        during string parsing with all possible prefixes (e.g. kg, mg, etc.).
        For all other base units, one can set 'register' to True, or manually
        register them with the 'register_unit()' method.

        Since the index argument is used as a list index, it is possible to
        give negative values. This makes adding dimensionless units more
        convenient. The first dimensionless base unit can be created with
        index=-1, the second with index=-2, etc.

        Creating a base unit is final. Once a base unit has been created,
        create_base_unit() will raise an exception, if the same index is used
        again.
        """
        if self._reg_base[index] is not None:
            raise BaseUnitExists()

        unit_vector = np.zeros(self._n_base)
        unit_vector[index] = 1
        base = Unit(1, unit_vector, label, symbol, latex, self)

        self._reg_base[index] = base
        
        if register:
            self.register_unit(base, label, symbol, latex)
        
        return base

    def create_unit(self, factor, unit_vector, label=None, symbol=None,
                    latex=None):
        """
        Creates and registers a new unit constructed from the given unit_vector and
        the factor. The newly created unit is returned.

        Please note that unlike create_base_unit(), all units created with
        this method are registered. 

        If registering this unit causes ambiguities, an exception is raised.
        An example of an ambiguity is adding a unit with symbol 'h' (hour) if
        Planck's quantum with symbol 'h' is already registered. An example of
        a more subtle ambiguity is, if one tries to add a unit with the symbol
        'min' (minutes) and there is already a unit 'in' (inch) and the prefix
        'm' (Milli).
        """
        unit = Unit(factor, unit_vector, label, symbol, latex, self)
        return self.register_unit(unit, label, symbol, latex)

    def register_unit(self, unit, label, symbol, latex=None):
        """
        Registers the given unit. Registering a unit means, that it is added
        to internal registry and will be considered when parsing a unit
        string. This method can be used to register anonymous units. The
        method returns the created unit.

        The same note about ambiguities for create_prefix() applies here.
        """
        if unit.unit_system() is not self:
            raise DifferentUnitSystem()

        for other_unit in self._reg_units_symbol.keys():
            for other_prefix in [""] + list(self._reg_prefixes_symbol.keys()):
                for this_prefix in [""] + \
                        list(self._reg_prefixes_symbol.keys()):
                    if other_prefix + other_unit == this_prefix + symbol:
                        raise SymbolCollision("Existing %s+%s conflicts with"
                                              " requested %s+%s." % \
                                              (repr(other_prefix),
                                               repr(other_unit),
                                               repr(this_prefix),
                                               repr(symbol)))

        copy = Unit(unit.factor(), unit.unit_vector(), label, symbol, latex,
                    self)
        copy._history = unit._history

        self._reg_units_all.append(copy)
        self._reg_units_label[label] = copy
        self._reg_units_symbol[symbol] = copy
        if latex is not None:
            self._reg_units_latex[latex] = copy
        
        return copy


    def create_prefix(self, factor, label=None, symbol=None, latex=None):
        """
        Creates and registers a new prefix built from the given factor. The
        newly created prefix is returned.

        If registering this prefix causes ambiguities, an exception is raised.
        An example of a ambiguity is, if one tries to add the 'm' (Milli)
        prefix, and there are already units with the symbols 'min' (minutes)
        and 'in' (inch).
        """
        prefix = Prefix(factor, label, symbol, latex, self)
        return self.register_prefix(prefix, label, symbol, latex)
        
    def register_prefix(self, prefix, label, symbol, latex=None):
        """
        Registers the given prefix. Registering a prefix means, that it is
        added to internal registry and will be considered when parsing a unit
        string. This method can be used to register anonymous prefixes.

        The same note about ambiguities for create_prefix() applies here. 
        """
        if prefix.unit_system() is not self:
            raise DifferentUnitSystem()

        if symbol in self._reg_prefixes_symbol:
            raise SymbolCollision("Conflict with existing prefix %s" % \
                                  repr(symbol))

        for other_unit in self._reg_units_symbol.keys():
            for other_prefix in [""] + list(self._reg_prefixes_symbol.keys()):
                for this_unit in self._reg_units_symbol.keys():
                    if other_prefix + other_unit == symbol + this_unit:
                        raise SymbolCollision("Existing %s+%s conflicts with"
                                              " requested %s+%s." % \
                                              (repr(other_prefix),
                                               repr(other_unit),
                                               repr(symbol),
                                               repr(this_unit)))

        copy = Prefix(prefix.factor(), label, symbol, latex, self)

        self._reg_prefixes_all.append(copy)
        self._reg_prefixes_label[label] = copy
        self._reg_prefixes_symbol[symbol] = copy
        if latex is not None:
            self._reg_prefixes_latex[latex] = copy
        
        return copy

        
    def dimensionless(self, unit):
        """
        Check whether the unit vector of the given unit is a pure linear
        combination of dimensionless base units. If so, return True,
        otherwise False.
        """
        return not (unit.unit_vector() * (1 - self._dimensionless_mask)).any()

    def parse_unit(self, expression):
        """
        Try to parser the given string to construct a unit from the string.
        The new unit is returned on success. In case of an error, an exception
        is raised.

        While parsing the string, the method searches all combinations of
        registered prefixes and registered units to identify the individual
        tokens. The method only tries to parse a single unit, optionally
        combined with a prefix.
        """
        if expression in self._reg_units_symbol.keys():
            return self._reg_units_symbol[expression]

        for prefix in self._reg_prefixes_symbol.keys():
            if expression.startswith(prefix):
                remainder = expression[len(prefix):]
                if remainder in self._reg_units_symbol.keys():
                    unit = self._reg_units_symbol[remainder]
                    prefix = self._reg_prefixes_symbol[prefix]
                    break
        else:
            raise UnitNotFound(expression)

        return Unit(prefix.factor() * unit.factor(),
                    unit.unit_vector(),
                    join_or_none(prefix.label(), unit.label()),
                    join_or_none(prefix.symbol(), unit.symbol()),
                    join_or_none(prefix.latex(), unit.latex()),
                    self)
                    

    def base_representation(self, unit_vector, lors=False):
        """
        Creates a string representation of the given unit vector using a
        product of powers of the base units.

        If the lors arguemnt is set to true, the method uses lors() of the
        base units. Otherwise symbol() is used. If there are undefined base
        units at the time of execution, these base units are represented by
        [base#i] where i is the index of the base unit.
        """
        assert len(unit_vector) == self._n_base

        factors = []

        for i, (base, power) in enumerate(zip(self._reg_base, unit_vector)):
            if base is None:
                base_str = "[base#%d]" % i
            elif lors:
                base_str = base.lors()
            else:
                base_str = base.symbol()
            if power == 1:
                factors.append(base_str)

            elif power > 0:
                if lors:
                    pattern = "%s^{%g}" 
                else:
                    pattern = "%s^%g" 

                factors.append(pattern % (base_str, power))

            elif power < 0:
                if lors:
                    pattern = "%s^{%g}" 
                else:
                    pattern = "%s^(%g)" 

                factors.append(pattern % (base_str, power))

        return " ".join(factors)

class Quantity(ModifiableNamedMixin, Named, SystemAffiliatedMixin):
    """
    The Quantity stores a single value annotated with an uncertainty and a
    unit. The Quantity class is the working horse of the pyveu package.

    Quantity objects support arithmetic operations with other Quantities,
    Units and prefixes. Each operation generates a new object. Quantities keep
    track of its dependencies and how it has been constructed. This
    information is used to keep track of correlations between quantities and
    to propagate uncertainties.

    Arithmetic operations involving quantities consider the units of all
    participants. This means, that for example an addition of two quantities is
    only possible, if they have the same unit. Multiplications yield a new
    quantity object with the product of both units.

    The error propagation is calculated when the arithmetic operation is
    executed. Modifying one of the participating quantities does not modify
    the resulting quantity.

    Internally, quantity objects store the value in base units. The unit is
    stored as a unit vector which specifies the exponents of the base units.
    In order to propagates the uncertainty each quantity needs to keep a list
    of all quantities it was initially derived from. Additionally, quantities
    store the uncertainties of these initial quantities and the partial
    derivatives of the quantity with respect to the initial quantities. 

    Initial quantities are creates with the Quantity() constructor. All
    quantities creates in this way are considered to be statistically
    independent. Quantities created by arithmetic operations are called
    dependent quantities, since their uncertainty depends on the initial
    independent quantities. Dependent quantities store the uncertainty of all
    the independent quantities it depends on, and the partial derivatives with
    respect to all independent quantities it depends on. The id() method is
    used to identify independent quantities.

    In-place arithmetic operations generate a new object, such that id()
    returns a different value. The returned object is a dependent quantity.
    This distinction is important in the following example
    >>> a = Quantity("10 += 1")
    >>> b = a + 3  # dependent quantity
    >>> a *= 2  # A has a different id()
    >>> c = a + 6

    Quantity b depends on quantity a. However, when the quantity a is
    multiplied in-place, a new quantity a is created, which depends on the
    initial quantity a. The third quantity c, which is derived from the new a,
    also becomes a quantity depending on the initial quantity a. When one
    combines b and c in an arithmetic operations, the framework knows that the
    both variables depend on the same initial quantity. 
    >>> 2 * a - c
    0 +- 0

    If the values had been modified in-place, leaving the id() unchanged, the
    resulting object would have an ambiguous value of the initial uncertainty
    of a.

    Quantity objects inherit all the properties from Named and
    SystemAffiliatedMixin. This means, Quantity object can be annotated with a
    label, symbol and latex alternative symbol. It is possible to modify the
    names using the label(), symbol() and latex() method. Furthermore,
    Quantity objects are tied to a unit system.

    The constructor has an optional argument unit_system. If it is omitted or
    set to None, the new Quantity object is tied to the unit system returned
    by pyveu.get_default_unit_system().

    Various methods accept the 'to' argument. This argument changes the unit
    on which the return value is based. For example, consider a quantity for
    the speed of a tennis ball.
    >>> v = Quantity("60 m/s")

    By default, the value() method returns the value in base units.
    >>> v.value()
    60

    If the 'to' argument is passed to the value method, one can retrieve the
    value in different units.
    >>> v.value(to="km/h")
    216.0
    """

    qid_counter = 1

    def __init__(self, value, error=None, unit=None, label=None, symbol=None,
                 latex=None, unit_system=None):
        """
        Creates a new, statistically independent quantity object.
        
        If the value argument is a
        string and error and unit are None, the value argument is parsed to
        obtain the value, the uncertainty and the unit of the quantity.
        Otherwise, value must be a number.

        The error argument defines the uncertainty of the quantity. If the
        value is a string, error must be None.

        The unit argument can be a unit object or a unit_vector. In any case
        value and error are assumed to be given in this unit.

        If the unit_system parameter is omitted, the quantity is tied to the
        unit system returned by pyveu.get_default_unit_system(). Otherwise,
        the given unit system is used. If the parameter is omitted but a unit
        object is given, the unit system of the unit object is used.
        """
        Named.__init__(self, label, symbol, latex)

        self._qid = Quantity.qid_counter
        Quantity.qid_counter += 1

        # resolve unit system
        if unit_system is None:
            if isinstance(unit, Unit):
                unit_system = unit.unit_system()
            else:
                unit_system = get_default_unit_system()
        else:
            if isinstance(unit, Unit):
                if unit.unit_system() is not unit_system:
                    raise DifferentUnitSystem()

        SystemAffiliatedMixin.__init__(self, unit_system)

        self._derivatives = {}
        self._variances = {}

        if isinstance(value, str):
            # parse quantity string
            if error is not None:
                raise ValueError("When value is a string, error must be None.")
            if unit is not None:
                raise ValueError("When value is a string, unit must be None.")

            value, error, unit_vector = Quantity.parse(value, unit_system)
            self._variance = error**2
            self._value = value
            self._unit_vector = unit_vector
        else:
            factor = 1

            # resolve unit
            if unit is None:
                self._unit_vector = np.zeros(unit_system._n_base)
            elif isinstance(unit, collections.Iterable):
                self._unit_vector = np.array(unit)
                if len(self._unit_vector) != unit_system._n_base:
                    raise ValueError("Unit vector length mismatch.")
            else:
                self._unit_vector = unit.unit_vector()
                factor = unit.factor()

            # resolve value
            self._value = value * factor

            # resolve error
            if error is None:
                error = 0

            if error < 0:
                raise ValueError("Error must be positive.")

            error *= factor
            self._variance = error**2

    def qid(self):
        """
        Returns an identifier of the quantity. The identifier is unique for
        the lifetime of the python process. The identifier is an integer. The
        qid is used to track the dependencies between quantities.
        """
        return self._qid

    def value(self, to=None):
        """
        Returns the value of the quantity object. If the optional argument
        'to' is omitted, the returned value is in base units. If a string or a
        unit object is given, the unit is returned in this unit. If the given
        unit is not a scalar multiple of this quantity, an exception is raised.
        """
        if to is None:
            return self._value
        elif isinstance(to, str):
            to = Quantity.parse_unit(to, self.unit_system())

        if to.unit_system() is not self.unit_system():
            raise DifferentUnitSystem()
        if (to.unit_vector() != self.unit_vector()).any():
            raise ValueError("Unit is not a scalar multiple.")
        return self._value / to.factor()


    def error(self, to=None):
        """
        Returns the uncertainty of the quantity object. If the optional argument
        'to' is omitted, the returned error is in base units. If a string or a
        unit object is given, the unit is returned in this unit. If the given
        unit is not a scalar multiple of this quantity, an exception is
        raised.

        The return value is the square root of variance().
        """
        return math.sqrt(self.variance(to))

    def variance(self, to=None):
        """
        Returns the variance of the quantity object. If the optional argument
        'to' is omitted, the returned error is in base units. If a string or a
        unit object is given, the unit is returned in this unit. If the given
        unit is not a scalar multiple of this quantity, an exception is
        raised.
        """
        if to is None:
            return self._variance
        elif isinstance(to, str):
            to = Quantity.parse_unit(to, self.unit_system())

        if to.unit_system() is not self.unit_system():
            raise DifferentUnitSystem()
        if (to.unit_vector() != self.unit_vector()).any():
            raise ValueError("Unit is not a scalar multiple.")
        return self._variance / to.factor()**2

    def round(self, to=None, significant_digits=1.2):
        """
        Returns the triple: rounded value as string, rounded error as string,
        common exponent as integer. This information can be used to construct
        string representations of the quantities.

        The value string is rounded to the last significant digit of the
        rounded error. The optional keywords significant_digits determines how
        the error should be rounded. If significant_digits is set to an
        integer, this corresponds to the number of significant digits of the
        error. If significant_digits is a float, the error is rounded to
        ceil(significant_digits) or floor(significant_digits), depending on
        the value of the error. For example, if significant_digits is 1.2,
        errors between 0.10 and 0.20 are rounded to two significant_digits,
        errors between 0.2 and 1.0 are rounded to one significant digit. The
        border between these two ranges is determined by the decimal part of
        significant_digits.

        Both, the value and the error, need to be multiplied with
        10^(common_exponent). This means the returned information can be used
        to construct a sting of the form

            (rounded_value +- rounded_error) * 10^(common_exponent).

        If the optional argument 'to' is omitted, the returned error is in
        base units. If a string or a unit object is given, the unit is
        returned in this unit. If the given unit is not a scalar multiple of
        this quantity, an exception is raised.
        """
        value = self.value(to)
        error = self.error(to)

        if significant_digits < 1:
            raise ValueError("Argument significant_digits must be >= 1.")

        if error == 0:
            if value == 0:
                return "0", "0", 0
            return str(value), "0", 0

        # Get error MSD
        error_msd_pos = Quantity._msd_position(error)

        # Determine (int) number of significant digits
        if not isinstance(significant_digits, int):
            is_int = False
            threshold = significant_digits - _floor(significant_digits)
            # 10**int form build ins doesn't work for negative values
            error_msd = error * math.pow(10, -error_msd_pos - 1)
            significant_digits = _floor(significant_digits)
            if error_msd < threshold:
                significant_digits += 1
        else:
            is_int = True

        # Determine round position (considering error after rounding)
        round_pos = error_msd_pos - significant_digits + 1

        last_digit = Quantity._get_digit(error, round_pos)
        rounded_error = _round(error, -round_pos)
        rounded_last_digit = Quantity._get_digit(rounded_error, round_pos)

        if last_digit == 9 and rounded_last_digit  == 0 and is_int:
            round_pos += 1

        # Extract common factor
        value_msd_pos = Quantity._msd_position(value)

        if value_msd_pos > 3 and error_msd_pos > 3:
            min_msd_pos = min(value_msd_pos, error_msd_pos)
            common_factor = int(min_msd_pos / 3) * 3
        elif value_msd_pos < -3 and error_msd_pos < -3:
            max_msd_pos = max(value_msd_pos, error_msd_pos)
            common_factor = int(max_msd_pos / 3) * 3
        else:
            common_factor = 0

        value /= math.pow(10, common_factor)
        error /= math.pow(10, common_factor)
        round_pos -= common_factor

        # Round error and value
        value = _round(value, -round_pos)
        error = _round(error, -round_pos)

        # Format string
        if round_pos < 0:
            value = "%.{}f".format(-round_pos) % value
            error = "%.{}f".format(-round_pos) % error
        else:
            value = "%d" % value
            error = "%d" % error

        return value, error, common_factor
    
    @staticmethod
    def _get_digit(number, position):
        """
        Return the digit at the given position. Consider 3352.429, the digit
        at position 1 is 5, the digit at position -3 is 9.
        """
        upper = _floor(simple_abs(number) * 10**(-position))
        lower = _floor(upper / 10) * 10

        return upper - lower

    @staticmethod
    def _msd_position(number):
        """
        Returns the position of the most significant digit of the given
        number. The most significant digit of 1 is at position zero, the most
        significant digit of 314 is 2.
        """
        return int(_floor(math.log10(simple_abs(number))))

    def str(self, to=1, significant_digits=1.2):
        """
        Returns a string containing the value, error and the unit of the
        quantity. The error is rounded to 1 significant digit (two between 1.0
        and 2.0), the value is rounded to the last significant digit of the
        error. By default, the value and error are returned in base units. If
        the optional argument 'to' is given, it is used to determine the
        desired unit. 'to' can be a string or a unit object. If the given unit
        is not a scalar multiple of this quantity, all the remaining terms are
        added to the unit string. Any factor included in 'to' is ignored.

        See round() for more information about significant_digits.
        """
        if isinstance(to, (int, float)):
            round_to = Unit.create_with_history(to, self.unit_vector(),
                                                 self.unit_system())
            remainder = round_to
        elif isinstance(to, str):
            to = Quantity.parse_unit(to, self.unit_system())

        if isinstance(to, Unit):
            remainder_vector = self.unit_vector() - to.unit_vector()
            
            remainder = Unit.create_with_history(1, remainder_vector,
                                                 self.unit_system())

            round_to = to * remainder

        value, error, common_factor = self.round(round_to, significant_digits)

        tokens = []

        if self.symbol():
            tokens.append(self.symbol())
            tokens.append("=")

        if error != "0":
            value_error = "%s +- %s" % (value, error)
        else:
            value_error = value

        if error != "0" and (self.unit_vector() != 0).any():
            value_error = "(%s)" % value_error

        tokens.append(value_error)

        if common_factor != 0:
            tokens.append("*")
            tokens.append("10^%d" % common_factor)
        
        if to != 1:
            tokens.append(to.str())

        has_remainder = remainder.factor() != 1 or remainder.unit_vector().any()

        if to != 1 and has_remainder:
            tokens.append("*")

        if has_remainder:
            tokens.append(remainder.str())

        return " ".join(tokens)


    def unit_vector(self):
        """
        Returns the unit vector.
        """
        return np.array(self._unit_vector)


    def dimensionless(self):
        """
        Check whether the unit vector of this quantity is dimensionless().
        Dimensionless quantities can be used in mathematical function such as
        Sine of the exponential function.
        """
        return self.unit_system().dimensionless(self)

    def __str__(self):
        """
        Same as Quantity.str() with default arguments.
        """
        return self.str()

    def __repr__(self):
        """
        Returns a string containing the label and symbol if present, the
        value error and unit in base units. Furthermore, the string contains
        the list of id() of all the quantities it depends on. An example of
        the string is
        
            <Quantity Velocity: v = (219.2 +- 10.0) m s^-1 | depends=[124323432]>
        """
        pre_colon = ["Quantity"]
        post_colon = []

        if self._label is not None:
            pre_colon.append(self._label)

        if self._symbol is not None:
            post_colon.append(self._symbol)
            post_colon.append("=")

        if self.error() != 0:
            value_error = "%g +- %g" % (self._value, self.error())
        else:
            value_error = "%g" % self._value
        
        if self.error() != 0 and (self._unit_vector != 0).any():
            post_colon.append("(%s)" % value_error)
        else:
            post_colon.append(value_error)

        base_repr = self._unit_system.base_representation(self._unit_vector)
        if len(base_repr):
            post_colon.append(base_repr)

        if len(self._derivatives) > 0:
            ids = [str(x) for x in sorted(self._derivatives)]
            post_colon.append("|")
            post_colon.append("depends=[%s]" % ", ".join(ids))

        return "<%s: %s>" % (" ".join(pre_colon), " ".join(post_colon))

    @staticmethod
    def parse(expression, unit_system=None):
        """
        Parses the expression and returns the triple: value, error and unit
        vector. The optional parameter determines the unit system. If it is
        omitted (or set to None), the default unit system is used.

        This is a static method. It should be called using the class.
        >>> Quantity.parse("125.09 +- 0.24 GeV")
        (125.09, 0.24, np.array(...))

        The syntax of the expression is intended to follow mathematical
        intuition. An expression consists of three parts. The first part
        specifies the value of a quantity. This part is mandatory. The value
        must be specified as an integer or a float. Syntax of the value is
        similar to the float syntax in python.

        The second part is optional and specifies the uncertainty of the
        value. If this part is included it must start with the string '+-'
        followed by another integer of float. The error must be positive.

        The final part specifies the unit. The method returns a unit vector of
        (0, 0, ..., 0) if this part is omitted. The unit part consists of an
        arbitrary number of unit specifiers. A unit specifier is a string
        consisting a registered unit and optionally a registered prefix. unit
        specifies can be raised to a power by appending '^' and the exponent.
        The exponent must be an integer or a float. If unit specifies are
        separated by spaces, they are multiplied.

        Unlike the regular mathematical notation, a slash '/' begins a
        denominator sequence. All space-separated unit specifiers following
        the slash are part of the denominator. Another slash '/' continues the
        denominator. To switch back to the numerator, use the star '*'. The
        following examples illustrate the denominator/numerator convention.
        The right hand side in the following examples follow the regular
        mathematical conventions.

            a / b c = a / (b * c)
            a / b / c = a / (b * c)
            a / b * c = (a * c) / b
            a c / b = (a * c) / b
            a * c / b = (a * c) / b

        To summarize: Everything to the right of a slash '/' before a star '*'
        is in the denominator, independently of the number of slashes.
        Everything to the right of a star '/' before a slash '/' is in the
        numerator, independently of the number of stars.

        Full expression strings look like this.
        
            "10.1 +- 0.3 mm / s" 
            "210 +- 2 m s^-1" 
            "3e8 kg / m^2" 
            "-42"
            "1e-3 +- 43e-5"
            "312 +- 21.1 kg m / s^2"
        
        Please note that the use of parentheses is not possible.
        """
        # default value
        if unit_system is None:
            unit_system = get_default_unit_system()

        # coarse regular expression
        number_re = r"[+-]?[0-9]+(\.[0-9]+)?(e[+-]?[0-9]+)?"
        unit_re = r"[a-zA-Z*/\s][a-zA-Z0-9\s/*^+.-]*"
        total_re = r"^\s*(?P<value>%s)(\s*\+-\s*(?P<error>%s))?(?P<unit>%s)?$"
        total_re %= (number_re, number_re, unit_re)

        match = re.match(total_re, expression)
        if not match:
            raise ValueError("Syntax error in '%s'." % expression)
        groups = match.groupdict()

        # handle value
        value_part = groups["value"]
        value = float(value_part)

        # handle error
        error_part = groups["error"]
        error_part = error_part if error_part is not None else 0
        error = float(error_part)

        if error < 0:
            raise ValueError("Error %g < 0, must be non-negative." % error)

        # handle unit
        unit_part = groups["unit"]

        if unit_part is not None:
            unit = Quantity.parse_unit(unit_part, unit_system)
            value *= unit.factor()
            error *= unit.factor()
            unit_vector = unit.unit_vector()
        else:
            unit_vector = np.zeros(unit_system._n_base)

        return value, error, unit_vector

    @staticmethod
    def parse_unit(unit_part, unit_system=None):
        """
        Parse the unit part of Quantity expression. See Quantity.parse() for
        more information about the syntax. The method returns a unit object.
        The history of the unit object reflects the structure of given string.

        If the optional argument unit_system is omitted, the default unit
        system is used.
        """
        # Default value
        if unit_system is None:
            unit_system = get_default_unit_system()

        unit_token_re = r"\s*((?P<op>[*/])|(?P<name>[a-zA-Z][a-zA-Z0-9]*)" \
                        r"(\^(?P<exp>[-+]?[0-9]+(\.[0-9]+)?))?)\s*" 
        unit_re = r"[a-zA-Z*/\s][a-zA-Z0-9\s/*^+.-]*"

        if not re.match("^(%s)*$" % unit_re, unit_part):
            raise ValueError("Error while parsing Unit string '%s'." %
                             unit_part)

        # loop over all unit specifier and operators
        unit_vector = np.zeros(unit_system._n_base)
        mode = +1  # -1 for denominator, +1 for numerator
        previous_op = False  # whether the previous token was a operator
        numerator_factors = []
        denominator_factors = []
        for unit_token in re.finditer(unit_token_re, unit_part):
            groups = unit_token.groupdict()

            # Found a '*'
            if groups["op"] == '*':
                if previous_op:
                    raise ValueError("Unexpected '*', expected unit.")
                previous_op = True
                mode = +1
                continue

            # Found a '/'
            if groups["op"] == '/':
                if previous_op:
                    raise ValueError("Unexpected '/', expected unit.")
                previous_op = True
                mode = -1
                continue

            # Found a unit
            if groups["name"] is not None:
                previous_op = False
                unit = unit_system.parse_unit(groups["name"])

                # calculate effective exponent
                exponent = groups["exp"]
                exponent = exponent if exponent is not None else 1
                exponent = float(exponent)
                exponent *= mode

                # merge with current result
                if exponent == 1:
                    numerator_factors.append(unit)
                elif exponent > 0:
                    numerator_factors.append(unit**exponent)
                elif exponent == -1:
                    denominator_factors.append(unit)
                elif exponent < 0:
                    denominator_factors.append(unit**(-exponent))

        if previous_op:
            raise ValueError("Trailing '*' or '/'.")

        if len(numerator_factors):
            result = numerator_factors[0]
            for factor in numerator_factors[1:]:
                result *= factor
        else:
            result = 1

        if len(denominator_factors):
            denominator = denominator_factors[0]
            for factor in denominator_factors[1:]:
                denominator *= factor
            result /= denominator

        if isinstance(result, (int, float)):
            if result == 1:
                result = unit_system._reg_base[0]**0
            else:
                result *= unit_system._reg_base[0]**0

        return result


    def __neg__(self):
        """
        Calculates the negative of this quantity and returns the result as a
        new dependent quantity. 
        """
        return self * (-1)

    def _generic_operation(self, other, value_handler,
                                d_dx_handler, unit_handler):
        """
        Generic multiplication operator. By passing appropriate handlers this
        method can be used for (right and left) multiplications and (right and
        left) divisions.

        Consider the generic operator #, and the generic operation c = a # b.
        The handler signatures are as follows:

            value_handler(a)
              -> Returns the value of the result: c

            d_dx_handler(a, da_dx)
              -> Returns the derivative dc_dx

            unit_handler(unit_vector_a, a, unit_system)
              -> Returns the unit_vector of c
        """
        if isinstance(other, (int, float)):
            other = Quantity(other, unit_system=self.unit_system())

        elif isinstance(other, Prefix):
            other = Quantity(other.factor(), unit_system=other.unit_system())

        elif isinstance(other, Unit):
            other = Quantity(other.factor(), 0, other.unit_vector(),
                             unit_system=other.unit_system())

        if other.unit_system() is not self.unit_system():
            raise DifferentUnitSystem()

        
        value = value_handler(self.value(), other.value())
        unit = unit_handler(self.unit_vector(),
                            other.unit_vector(),
                            self.value(),
                            other.value(),
                            self.unit_system())
        result = Quantity(value,
                          0,  # Will operate on variance and derivatives
                          unit,
                          unit_system=self.unit_system())

        if self._variances:
            variances_self = self._variances
            derivatives_self = self._derivatives
        elif self.variance() > 0:
            variances_self = {self.qid(): self.variance()}
            derivatives_self = {self.qid(): 1}
        else:
            variances_self = {}
            derivatives_self = {}
                        
        if other._variances:
            variances_other = other._variances
            derivatives_other = other._derivatives
        elif other.variance() > 0:
            variances_other = {other.qid(): other.variance()}
            derivatives_other = {other.qid(): 1}
        else:
            variances_other = {}
            derivatives_other = {}

        dependencies = set(variances_self.keys()).union(variances_other.keys())

        result._variance = 0
        for dependency in dependencies:
            if dependency in variances_self and  dependency in variances_other:
                if variances_self[dependency] != variances_other[dependency]:
                    raise ValueError("This is a bug. Two quantities stored "
                                     "different variances for the same qid.")

            # Implementation of the chain rule
            derivative = d_dx_handler(self.value(), other.value(),
                                      derivatives_self.get(dependency, 0),
                                      derivatives_other.get(dependency, 0))

            if dependency in variances_self:
                variance = variances_self[dependency]
            else:
                variance = variances_other[dependency]

            if variance == 0 or derivative == 0:
                continue

            result._variance += variance * derivative**2
            result._variances[dependency] = variance
            result._derivatives[dependency] = derivative

        return result


    @staticmethod
    def _mul_value_handler(a, b):
        """
        Helper method for multiplcations. Combines the two values.
        """
        return a * b

    @staticmethod
    def _mul_d_dx_handler(a, b, da_dx, db_dx):
        """
        Helper method for multiplcations. Computes a combined derication.
        """
        return a * db_dx + da_dx * b

    @staticmethod
    def _mul_unit_handler(unit_vector_a, unit_vector_b, a, b, unit_system):
        """
        Helper method for multiplcations. Computes a combined derication.
        """
        return unit_vector_a + unit_vector_b

    def __mul__(self, other):
        """
        Multiplies the Quantity with an other Quantity, Unit or prefix. This
        multiplies the values, propagates the errors and multiplies the unit.
        The method returns a new Quantity.
        """
        return self._generic_operation(other,
                                       self._mul_value_handler,
                                       self._mul_d_dx_handler,
                                       self._mul_unit_handler)

    def __rmul__(self, other):
        """
        Multiplication where this object is one the right. There is no
        difference between left- and right-multiplication.
        """
        return self * other
        
    @staticmethod
    def _div_value_handler(a, b):
        """
        Helper method for divisions. Combines the two values.
        """
        return a / b

    @staticmethod
    def _div_d_dx_handler(a, b, da_dx, db_dx):
        """
        Helper method for divisions. Computes a combined derication.
        """
        return da_dx / b - a / b**2 * db_dx

    @staticmethod
    def _div_unit_handler(unit_vector_a, unit_vector_b, a, b, unit_system):
        """
        Helper method for divisions. Computes a combined derication.
        """
        return unit_vector_a - unit_vector_b

    def __truediv__(self, other):
        """
        Divides the Quantity with an other Quantity, Unit or prefix. This
        divides the values, propagates the errors and divides the unit.
        The method returns a new Quantity.
        """
        return self._generic_operation(other,
                                       self._div_value_handler,
                                       self._div_d_dx_handler,
                                       self._div_unit_handler)

    @staticmethod
    def _rdiv_value_handler(a, b):
        """
        Helper method for divisions. Combines the two values.
        """
        return Quantity._div_value_handler(b, a)

    @staticmethod
    def _rdiv_d_dx_handler(a, b, da_dx, db_dx):
        """
        Helper method for divisions. Computes a combined derication.
        """
        return Quantity._div_d_dx_handler(b, a, db_dx, da_dx)

    @staticmethod
    def _rdiv_unit_handler(unit_vector_a, unit_vector_b, a, b, unit_system):
        """
        Helper method for divisions. Computes a combined derication.
        """
        return Quantity._div_unit_handler(unit_vector_b, unit_vector_a,
                                          b, a, unit_system)

    def __rtruediv__(self, other):
        """
        Divides the Quantity with an other Quantity, Unit or prefix. This
        divides the values, propagates the errors and divides the unit.
        The method returns a new Quantity.
        """
        return self._generic_operation(other,
                                       self._rdiv_value_handler,
                                       self._rdiv_d_dx_handler,
                                       self._rdiv_unit_handler)

    def __div__(self, other):
        """
        Compatibility with Python 2.7. 

        The standard division (/) in Python 2.7 calls this method. Dividing a
        Quantity by an integer should not floor the value.
        """
        return self.__truediv__(other)

    def __rdiv__(self, other):
        """
        Compatibility with Python 2.7. 

        The standard division (/) in Python 2.7 calls this method. Dividing a
        Quantity by an integer should not floor the value.
        """
        return self.__rtruediv__(other)

    @staticmethod
    def _add_value_handler(a, b):
        """
        Helper method for additions. Combines the two values.
        """
        return a + b

    @staticmethod
    def _add_d_dx_handler(a, b, da_dx, db_dx):
        """
        Helper method for additions. Computes a combined derivations.
        """
        return da_dx + db_dx

    @staticmethod
    def _add_unit_handler(unit_vector_a, unit_vector_b, a, b, unit_system):
        """
        Helper method for additions. Computes a combined unit vectors.
        """
        unit_a = Unit(1, unit_vector_a, None, None, None, unit_system)
        unit_b = Unit(1, unit_vector_b, None, None, None, unit_system)

        if unit_a.dimensionless() and (unit_vector_b == 0).all():
            # Adding integer to dimensionless, this is fine.
            return unit_vector_a
        elif unit_b.dimensionless() and (unit_vector_a == 0).all():
            # Same here, roles swapped
            return unit_vector_b
        elif (unit_vector_a != unit_vector_b).any():
            # Otherwise unit vectors need to be identical
            raise ValueError("Cannot add %s and %s." %
                             (unit_a.base_representation(),
                              unit_b.base_representation()))
        else:
            return unit_vector_a

    def __add__(self, other):
        """
        Adds a Quantity and another Quantity, Unit or prefix. This
        adds the values, propagates the errors. Units need to identical or
        dimensionless.

        The method returns a new Quantity.
        """
        return self._generic_operation(other,
                                       self._add_value_handler,
                                       self._add_d_dx_handler,
                                       self._add_unit_handler)

    def __radd__(self, other):
        """
        Addition where this object is one the right. There is no
        difference between left- and right-addition.
        """
        return self + other


    @staticmethod
    def _sub_value_handler(a, b):
        """
        Helper method for subtractions. Combines the two values.
        """
        return a - b

    @staticmethod
    def _sub_d_dx_handler(a, b, da_dx, db_dx):
        """
        Helper method for subtractions. Computes a combined derivations.
        """
        return da_dx - db_dx

    def __sub__(self, other):
        """
        Adds a Quantity and another Quantity, Unit or prefix. This
        adds the values, propagates the errors. Units need to identical or
        dimensionless.

        The method returns a new Quantity.
        """
        return self._generic_operation(other,
                                       self._sub_value_handler,
                                       self._sub_d_dx_handler,
                                       self._add_unit_handler)
    @staticmethod
    def _rsub_value_handler(a, b):
        """
        Helper method for subtractions. Combines the two values.
        """
        return Quantity._sub_value_handler(b, a)

    @staticmethod
    def _rsub_d_dx_handler(a, b, da_dx, db_dx):
        """
        Helper method for subtractions. Computes a combined derivations.
        """
        return Quantity._sub_d_dx_handler(b, a, db_dx, da_dx)

    def __rsub__(self, other):
        """
        Subtraction where this object is one the right.
        """
        return self._generic_operation(other,
                                       self._rsub_value_handler,
                                       self._rsub_d_dx_handler,
                                       self._add_unit_handler)

    @staticmethod
    def _pow_value_handler(a, b):
        """
        Helper method for exponentiations. Combines the two values.
        """
        if a <= 0 and _floor(b) != b:
            raise ValueError("Cannot raise negative number to "
                             "a fractional power.") 

        return a**b

    @staticmethod
    def _pow_d_dx_handler(a, b, da_dx, db_dx):
        """
        Helper method for exponentiations. Computes a combined derivations.
        """
        if a <= 0 and db_dx != 0:
            raise UncertaintyIllDefined("Base cannot be negative when "
                                        "exponent has uncertainty.")

        result = 0

        if da_dx != 0:
            if a == 0 and b < 1:
                raise UncertaintyIllDefined("Base cannot be zero with "
                                            "uncertainty when "
                                            "exponent is less than one.")

            result += b * a**(b - 1) * da_dx 
            
        if db_dx != 0:
            result += a**b * np.log(a) * db_dx

        return result

    @staticmethod
    def _pow_unit_handler(unit_vector_a, unit_vector_b, a, b, unit_system):
        """
        Helper method for exponentiations. Computes a combined unit vectors.
        """
        unit_b = Unit(1, unit_vector_b, None, None, None, unit_system)

        if not unit_b.dimensionless():
            raise ValueError("Exponent '%s' is not dimensionless." %
                              unit_b.base_representation())
        else:
            return unit_vector_a * b

    def __pow__(self, power):
        """
        Calculates a power of this quantity and returns the result as a new
        dependent quantity. The other operand can be a number, a prefix, a or
        a quantity.  If it is a unit or a quantity, it must be
        dimensionless().
        """
        return self._generic_operation(power,
                                       self._pow_value_handler,
                                       self._pow_d_dx_handler,
                                       self._pow_unit_handler)

    @staticmethod
    def _rpow_value_handler(a, b):
        """
        Helper method for exponentiations. Combines the two values.
        """
        return Quantity._pow_value_handler(b, a)

    @staticmethod
    def _rpow_d_dx_handler(a, b, da_dx, db_dx):
        """
        Helper method for exponentiations. Computes a combined derivations.
        """
        return Quantity._pow_d_dx_handler(b, a, db_dx, da_dx)

    @staticmethod
    def _rpow_unit_handler(unit_vector_a, unit_vector_b, a, b, unit_system):
        """
        Helper method for exponentiations. Computes a combined unit vectors.
        """
        return Quantity._pow_unit_handler(unit_vector_b, unit_vector_a,
                                   b, a, unit_system)

    def __rpow__(self, power):
        """
        Calculates a power of this quantity and returns the result as a new
        dependent quantity. The other operand can be a number, a prefix, a or
        a quantity.  If it is a unit or a quantity, it must be
        dimensionless().
        """
        return self._generic_operation(power,
                                       self._rpow_value_handler,
                                       self._rpow_d_dx_handler,
                                       self._rpow_unit_handler)


def _generic_function(argument, value_handler, d_dx_handler, unit_handler):
    """
    Generic function. By passing appropriate handlers, this
    method can be used for generic mathematical functions.

    Consider the generic function f, and the generic calculation c = f(a)
    The handler signatures are as follows:

        value_handler(a)
          -> Returns the value of the result: c

        d_dx_handler(a, da_dx)
          -> Returns the derivative dc_dx

        unit_handler(unit_vector_a, a, unit_system)
          -> Returns the unit_vector of c
    """
    if isinstance(argument, (int, float)):
        argument = Quantity(argument)

    elif isinstance(argument, Prefix):
        argument = Quantity(argument, unit_system=argument.unit_system())

    elif isinstance(argument, Unit):
        argument = Quantity(argument.factor(), 0, argument.unit_vector(),
                         unit_system=argument.unit_system())

    value = value_handler(argument.value())
    unit = unit_handler(argument.unit_vector(),
                        argument.value(),
                        argument.unit_system())
    result = Quantity(value,
                      0,  # Will operate on variance and derivatives
                      unit,
                      unit_system=argument.unit_system())

    if argument._variances:
        variances = argument._variances
        derivatives = argument._derivatives
    elif argument.variance() > 0:
        variances = {argument.qid(): argument.variance()}
        derivatives = {argument.qid(): 1}
    else:
        variances = {}
        derivatives = {}
                    
    result._variance = 0
    for dependency in variances:
        variance = variances[dependency]

        # Implementation of the chain rule
        derivative = d_dx_handler(argument.value(), derivatives[dependency])
        if derivative == 0:
            continue

        result._variance += variance * derivative**2
        result._variances[dependency] = variance
        result._derivatives[dependency] = derivative

    return result

################################################################################
# Exponential function
def _exp_value_handler(a):
    """
    Calculates value of expoential function.
    """
    return math.exp(a)

def _exp_d_dx_handler(a, da_dx):
    """
    Calculates the derivative d/dx exp(a(x)).
    """
    return math.exp(a) * da_dx
    
def _no_unit_handler(unit_vector, a, unit_system):
    """
    Check that the unit vector is dimensionless and return a zero unit vector.
    """
    unit = Unit(1, unit_vector, None, None, None, unit_system)
    if not unit.dimensionless():
        raise ValueError("Operand '%s' is not dimensionless." %
                          unit.base_representation())

    return unit_vector * 0

def exp(quantity):
    """
    Calculates the exponential of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return _generic_function(quantity,
                             _exp_value_handler,
                             _exp_d_dx_handler,
                             _no_unit_handler)
    
################################################################################
# Natural logarithm
def _log_value_handler(a):
    """
    Calculates value of natural logaritm.
    """
    if a <= 0:
        raise ValueError("Argument of log must be positive.")
    return math.log(a)

def _log_d_dx_handler(a, da_dx):
    """
    Calculates the derivative d/dx log(a(x)).
    """
    return da_dx / a

def log(quantity):
    """
    Calculates the natural logarithm of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return _generic_function(quantity,
                             _log_value_handler,
                             _log_d_dx_handler,
                             _no_unit_handler)

################################################################################
# Logaritm to the base 2
def log2(quantity):
    """
    Calculates the logarithm to the base 2 of the given quantity and
    propagates the uncertainty. The quantity has to be dimensionless.
    """
    return 1 / math.log(2) * _generic_function(quantity,
                                               _log_value_handler,
                                               _log_d_dx_handler,
                                               _no_unit_handler)

################################################################################
# Logaritm to the base 10
def log10(quantity):
    """
    Calculates the logarithm to the base 10 of the given quantity and
    propagates the uncertainty. The quantity has to be dimensionless.
    """
    return 1 / math.log(10) * _generic_function(quantity,
                                                _log_value_handler,
                                                _log_d_dx_handler,
                                                _no_unit_handler)

################################################################################
# Power
def pow(base, exponent):
    """
    Calculates the power the given quantity and propagates the uncertainty.
    The exponent has to be dimensionless. See Quantity's power operator.
    """
    return base**exponent

################################################################################
# Square root
def sqrt(quantity):
    """
    Calculates the square root of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return quantity**0.5

################################################################################
# Sine
def _sin_value_handler(a):
    """
    Calculates the sine of a.
    """
    return math.sin(a)

def _sin_d_dx_handler(a, da_dx):
    """
    Calculates the derivative d/dx sin(a(x)).
    """
    return da_dx * math.cos(a)

def sin(quantity):
    """
    Calculates the sine of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return _generic_function(quantity,
                             _sin_value_handler,
                             _sin_d_dx_handler,
                             _no_unit_handler)

################################################################################
# Cosine
def _cos_value_handler(a):
    """
    Calculates the cosine of a.
    """
    return math.cos(a)

def _cos_d_dx_handler(a, da_dx):
    """
    Calculates the derivative d/dx cos(a(x)).
    """
    return -da_dx * math.sin(a)

def cos(quantity):
    """
    Calculates the cosine of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return _generic_function(quantity,
                             _cos_value_handler,
                             _cos_d_dx_handler,
                             _no_unit_handler)

################################################################################
# Tangent
def tan(quantity):
    """
    Calculates the tangent of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return sin(quantity) / cos(quantity)

################################################################################
# Hyperbolic sine
def _sinh_value_handler(a):
    """
    Calculates the hyperbolic sine of a.
    """
    return math.sinh(a)

def _sinh_d_dx_handler(a, da_dx):
    """
    Calculates the derivative d/dx sinh(a(x)).
    """
    return da_dx * math.cosh(a)

def sinh(quantity):
    """
    Calculates the hyperblic sine of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return _generic_function(quantity,
                             _sinh_value_handler,
                             _sinh_d_dx_handler,
                             _no_unit_handler)

################################################################################
def _cosh_value_handler(a):
    """
    Calculates the hyperbolic sine of a.
    """
    return math.cosh(a)

def _cosh_d_dx_handler(a, da_dx):
    """
    Calculates the derivative d/dx sinh(a(x)).
    """
    return da_dx * math.sinh(a)

def cosh(quantity):
    """
    Calculates the hyperbolic cosine of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return _generic_function(quantity,
                             _cosh_value_handler,
                             _cosh_d_dx_handler,
                             _no_unit_handler)


################################################################################
# Hyperbolic tangent
def tanh(quantity):
    """
    Calculates the hyperbolic tangent of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return sinh(quantity) / cosh(quantity)

################################################################################
# Inverse sine
def _asin_value_handler(a):
    """
    Calculates the inverse sine of a.
    """
    return math.asin(a)

def _asin_d_dx_handler(a, da_dx):
    """
    Calculates the derivative d/dx asin(a(x)).
    """
    return da_dx / math.sqrt(1 - a**2)

def asin(quantity):
    """
    Calculates the inverse sine of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return _generic_function(quantity,
                             _asin_value_handler,
                             _asin_d_dx_handler,
                             _no_unit_handler)

################################################################################
# Inverse cosine
def _acos_value_handler(a):
    """
    Calculates the inverse cosine of a.
    """
    return math.acos(a)

def _acos_d_dx_handler(a, da_dx):
    """
    Calculates the derivative d/dx acos(a(x)).
    """
    return -da_dx / math.sqrt(1 - a**2)

def acos(quantity):
    """
    Calculates the inverse cosine of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return _generic_function(quantity,
                             _acos_value_handler,
                             _acos_d_dx_handler,
                             _no_unit_handler)

################################################################################
# Inverse tangent
def _atan_value_handler(a):
    """
    Calculates the inverse tangent of a.
    """
    return math.atan(a)

def _atan_d_dx_handler(a, da_dx):
    """
    Calculates the derivative d/dx atan(a(x)).
    """
    return da_dx / (1 + a**2)

def atan(quantity):
    """
    Calculates the inverse tangent of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return _generic_function(quantity,
                             _atan_value_handler,
                             _atan_d_dx_handler,
                             _no_unit_handler)

################################################################################
# Inverse hyperbolic sine
def asinh(quantity):
    """
    Calculates the inverse hyperbolic sine of the given quantity and
    propagates the uncertainty. The quantity has to be dimensionless.
    """
    return log(quantity + sqrt(quantity**2 + 1))

def acosh(quantity):
    """
    Calculates the inverse hyperbolic cosine of the given quantity and
    propagates the uncertainty. The quantity has to be dimensionless.
    """
    return log(quantity + sqrt(quantity**2 - 1))

def atanh(quantity):
    """
    Calculates the inverse hyperbolic tangent of the given quantity and
    propagates the uncertainty. The quantity has to be dimensionless.
    """
    return 0.5 * log((1 + quantity) / (1 - quantity))


################################################################################
# Absolute value

# Backup builtin absolute value function
simple_abs = abs

def _abs_value_handler(a):
    """
    Calculates value of expoential function.
    """
    return simple_abs(a)

def _abs_d_dx_handler(a, da_dx):
    """
    Calculates the derivative d/dx exp(a(x)).
    """
    if a == 0:
        raise UncertaintyIllDefined("Argument of abs() cannot be zero.")
    elif a < 0:
        return -da_dx
    else:
        return da_dx
    
def _abs_unit_handler(unit_vector, a, unit_system):
    """
    Check that the unit vector is dimensionless and return a zero unit vector.
    """
    return unit_vector 

def abs(quantity):
    """
    Calculates the absolute value of the given quantity and propagates the
    uncertainty. The quantity has to be dimensionless.
    """
    return _generic_function(quantity,
                             _abs_value_handler,
                             _abs_d_dx_handler,
                             _abs_unit_handler)


class QuantityArray(Quantity):
    """
    QuantityArrays are similar to regular Quantities, however they can store
    numpy arrays as values and/or error.
    """
    
    def from_list(self):
        """
        Builds a QuantityArray based on a list of Quantity objects. This
        method makes QuantityBuffers obsolete.
        """
        pass


# Stores the default unit system used by Quantity if the unit system argument
# is omitted. The variable is returned by get_default_unit_system(). This can
# be overwritten after importing the package.
default_unit_system = None

def get_default_unit_system():
    """
    Returns the variable default_unit_system. If the variable is None, it is
    initialized with the SI unit system.
    """
    global default_unit_system
    if default_unit_system is None:
        import pyveu.si
        default_unit_system = si.unit_system

    return default_unit_system
    

################################################################################
# Exceptions

class PyVeuException(Exception):
    """
    Base class from which all package-specific exceptions will be derived.
    """
    pass

class DifferentUnitSystem(PyVeuException):
    """
    This exception will be raises if an arithmetic operation is requested
    between two objects tied to different unit systems.
    """
    def __init__(self):
        super(DifferentUnitSystem, self).__init__(
            "Operations with two objects assigned to different unit systems"
            " are not permitted.")

class BaseUnitExists(PyVeuException):
    """
    This exception will be raises if one tries to overwrite a base unit.
    """
    def __init__(self):
        super(BaseUnitExists, self).__init__(
            "Base unit with this index exists. Base units can not be "
            "overwritten.")

class SymbolCollision(PyVeuException):
    """
    This exception is raised when one tried to add a unit/prefix which causes
    ambiguities in the unit system.
    """
    pass


class UnitNotFound(PyVeuException):
    """
    This exception is raised when parse_unit() is not able to find a unit (and
    prefix) to match the given expression.
    """
    pass

class UncertaintyIllDefined(PyVeuException):
    """
    Raises when the error propagation cannot be performed for the given
    values.
    """
    pass
