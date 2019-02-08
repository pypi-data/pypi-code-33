# coding utf-8

"""
Les unités de mesures de ce module respectent les définitons données
dans [wikipédia](https://fr.wikipedia.org/wiki/Unit%C3%A9_de_mesure)
"""

import enum


class Unit(enum.Enum):
    """
    Classe de base pour définir des unités de mesure.
    Inspirée de *Python Standard Library*, § DataTypes, enum.
    """
    def __new__(cls, val, symbol):
        obj = object.__new__(cls)
        obj._value_ = val
        obj._symbol = symbol
        return obj
    def convert(self, value, other):
        raise NotImplementedError
    @property
    def symbol(self): return self._symbol


_units_map = {}

class OrderUnit(Unit):
    """
    Classe de base pour les unités de mesures qui ont des
    multiples et sous multiples.

    Inspiré de *Python Standard Library*, § DataTypes, enum.
    """
    def convert(self, value, other):
        """
        Si *value* est exprimée dans le multiple *self*,
        retourne cette valeur exprimée dans un *other* multiple.
        Par exemple, pour les multiples du mètre:
        ```
        >>> Meter.kilometre.convert(10, Meter.metre)
        >>> 10000
        ```
        """
        other = self._match(other)
        if other is NotImplemented: raise ValueError
        return value*(10**(self.value - other.value))
    def _match(self, other):
        if self.__class__ is other.__class__: return other
        return _units_map.get(other, NotImplemented)
    def __ge__(self, other):
        other = self._match(other)
        return other if other is NotImplemented else self.value >= other.value
    def __gt__(self, other):
        other = self._match(other)
        return other if other is NotImplemented else self.value > other.value
    def __le__(self, other):
        other = self._match(other)
        return other if other is NotImplemented else self.value <= other.value
    def __lt__(self, other):
        other = self._match(other)
        return other if other is NotImplemented else self.value < other.value
    def __eq__(self, other):
        other = self._match(other)
        return other if other is NotImplemented else super().__eq__(other)
    def __hash__(self): return super().__hash__()

class Meter(OrderUnit):
    """
    Définit l'énumaration des multiples de l'unité de mesure du **mètre**
    selon [wikipedia](https://fr.wikipedia.org/wiki/M%C3%A8tre)
    """
    yoctometre  = (-24, 'ym')
    zeptometre  = (-21, 'zm')
    attometre   = (-18, 'am')
    femtometre  = (-15, 'fm')
    picometre   = (-12, 'pm')
    nanometre   = ( -9, 'nm')
    micormetre  = ( -6, 'µm')
    millimetre  = ( -3, 'mm')
    centimetre  = ( -2, 'cm')
    decimetre   = ( -1, 'dm')
    metre       = (  0, 'm')
    decametre   = (  1, 'dam')
    hectometre  = (  2, 'hm')
    kilometre   = (  3, 'km')
    megametre   = (  6, 'Mm')
    gigametre   = (  9, 'Gm')
    terametre   = ( 12, 'Tm')
    petametre   = ( 15, 'Pm')
    exametre    = ( 18, 'Em')
    zettametre  = ( 21, 'Zm')
    yottametre  = ( 24, 'Ym')
    
class Kilogram(OrderUnit):
    """
    Définit l'énumaration des multiples de l'unité de mesure du **kilogramme**
    selon [wikipedia](https://fr.wikipedia.org/wiki/Kilogramme)

    Seuls sont définis:
     * la tonne (Mégagramme) comme multiples;
     * les sous-multiples les plus utilisés.
    """
    microgram =  ( -9, 'µg') 
    milligram =  ( -6, 'mg')
    centigram =  ( -5, 'cg')
    decigram  =  ( -4, 'dg')
    gram      =  ( -3, 'g')
    decagram  =  ( -2, 'dag')
    hectogram =  ( -1, 'hg')
    kilogram  =  (  0, 'kg')
    tonne     =  (  3, 't')


class SquareMeter(OrderUnit):
    """
    Définit l'énumaration des multiples de l'unité de mesure du **Mètre carré**
    selon [wikipedia](https://fr.wikipedia.org/wiki/M%C3%A8tre_carr%C3%A9)    
    """
    millimeter_square = ( -6, 'mm²')
    centimeter_square = ( -4, 'cm²')
    decimeter_square  = ( -2, 'dm²')
    meter_square      = (  0, 'm²')   # == centiare
    centiare          = (  0, 'ca')   
    decameter_square  = (  2, 'dm²')  # == are
    are               = (  2, 'a') 
    hectometer_square = (  4, 'hm²')  # == hectare
    hectare           = (  4, 'ha')
    kilometer_square  = (  6, 'km²')
    

class CubicMeter(OrderUnit):
    """
    Définit l'énumaration des multiples de l'unité de mesure du **Mètre Cube**
    selon [wikipedia](https://fr.wikipedia.org/wiki/M%C3%A8tre_cube)    
    """
    cubic_millimeter = (-9, 'mm3')
    cubic_centimeter = (-6, 'cm3')
    cubic_decimeter  = (-3, 'dm3')
    cubic_meter      = ( 0, 'm3')
    cubic_decameter  = ( 3, 'dam3')
    cubic_hectometer = ( 6, 'hm3')
    cubic_kilometer  = ( 9, 'km3')

class Liter(OrderUnit):
    """
    Définit l'énumaration des multiples de l'unité de mesure du **Litre**
    selon [wikipedia](https://fr.wikipedia.org/wiki/Litre)    
    """
    milliliter      = (-3, 'ml')
    centiliter      = (-2, 'cl')
    deciliter       = (-1, 'dl')
    liter           = ( 0, 'l')
    hectoliter      = ( 2, 'hl')

_units_map[Liter.liter] = CubicMeter.cubic_decimeter
_units_map[Liter.milliliter] = CubicMeter.cubic_millimeter
_units_map[CubicMeter.cubic_decimeter] = Liter.liter
_units_map[CubicMeter.cubic_millimeter] = Liter.milliliter

class SpeedUnit(Unit):
    """
    Définit l'énumaration des multiples de l'unité de mesure du **Litre**
    selon [wikipedia](https://fr.wikipedia.org/wiki/M%C3%A8tre_par_seconde) et
    [wikipedia](https://fr.wikipedia.org/wiki/Kilom%C3%A8tre_par_heure) 
    """
    meter_per_second = (0, 'm/s')
    kilometer_per_hour = (1, 'km/h')
    def convert(self, value, other):
        """
        Si *value* est exprimée dans une des deux grandeurs,
        retourne cette valeur exprimée dans l'*other*.
        """
        if (self, other) == (SpeedUnit.meter_per_second, SpeedUnit.kilometer_per_hour):
            return value*3.6
        if (self, other) == (SpeedUnit.kilometer_per_hour, SpeedUnit.meter_per_second):
            return value/3.6
        raise ValueError

class TemperatureUnit(Unit):
    celcius = (0, '°C')
    kelvin  = (1, 'K')
    def convert(self, value, other):
        """
        Si *value* est exprimée dans une des deux grandeurs,
        retourne cette valeur exprimée dans l'*other*.
        """
        if  (self, other) == (TemperatureUnit.celcius, TemperatureUnit.kelvin):
            return value+273.15
        if  (self, other) == (TemperatureUnit.kelvin, TemperatureUnit.celcius):
            return value-273.15
        raise ValueError

__all__ = (
    "Unit",
    "Meter",
    "Kilogram",
    "SquareMeter",
    "CubicMeter",
    "Liter",
    "SpeedUnit",
    "TemperatureUnit",
    )


