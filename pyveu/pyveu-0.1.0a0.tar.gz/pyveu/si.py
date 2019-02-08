# coding=utf-8

# Copyright (C) 2018 Frank Sauerburger

import scipy.constants as sc
import pyveu


def create_systeme_international():
    """
    Creates a new SI unit system with the common units and prefixes. Returns
    the triple: unit system, prefix dict, unit dict.

    The returned unit system contains certain non-si units for convenience,
    such as minute, speed of light and electron volt, ...
    """

    si = pyveu.UnitSystem("Systeme International", 8, n_dimensionless=1)

    # Base units
    metre = si.create_base_unit(0, "Metre", "m", register=True)
    kilogram = si.create_base_unit(1, "Kilogram", "kg")
    second = si.create_base_unit(2, "Second", "s", register=True)
    ampere = si.create_base_unit(3, "Ampere", "A", register=True)
    kelvin = si.create_base_unit(4, "Kelvin", "K", register=True)
    mole = si.create_base_unit(5, "Mole", "mol", register=True)
    candela = si.create_base_unit(6, "Candela", "cd", register=True)
    radian = si.create_base_unit(-1, "Radian", "rad", register=True)

    gram = si.register_unit(kilogram / 1000, "Gram", "g")

    # Prefixes
    yocto = si.create_prefix(1e-24, "Yocto", "y")
    zepto = si.create_prefix(1e-21, "Zepto", "z")
    atto = si.create_prefix(1e-18, "Atto", "a")
    femto = si.create_prefix(1e-15, "Femto", "f")
    pico = si.create_prefix(1e-12, "Pico", "p")
    nano = si.create_prefix(1e-9, "Nano", "n")
    micro = si.create_prefix(1e-6, "Micro", "u", r"\mu")
    milli = si.create_prefix(1e-3, "Milli", "m")
    centi = si.create_prefix(1e-2, "Centi", "c")
    deci = si.create_prefix(1e-1, "Deci", "d")

    deca = si.create_prefix(10, "Deca", "da")
    hecto = si.create_prefix(100, "Hecto", "h")
    kilo = si.create_prefix(1000, "Kilo", "k")
    mega = si.create_prefix(1e6, "Mega", "M")
    giga = si.create_prefix(1e9, "Giga", "G")
    tera = si.create_prefix(1e12, "Tera", "T")
    peta = si.create_prefix(1e15, "Peta", "P")
    exa = si.create_prefix(1e18, "Exa", "E")
    zetta = si.create_prefix(1e21, "Zetta", "Z")
    yotta = si.create_prefix(1e24, "Yotta", "Y")
    
    # Derived units for convenience
    newton = si.register_unit(kilogram * metre / second**2, "Newton", "N")
    joule = si.register_unit(newton * metre, "Joule", "J")
    watt = si.register_unit(joule / second, "Watt", "W")
    volt = si.register_unit(watt / ampere, "Volt", "V")
    coulomb = si.register_unit(ampere * second, "Coulomb", "C")
    ohm = si.register_unit(volt / ampere, "Ohm", "ohm", "\\Omega")
    farad = si.register_unit(coulomb / volt, "Farad", "F")
    henry = si.register_unit(volt * second / ampere, "Henry", "H")
    tesla = si.register_unit(newton * second / (coulomb * metre), "Tesla", "T")
    weber = si.register_unit(tesla * metre**2, "Weber", "Wb")
    hertz = si.register_unit(1 / second, "Hertz", "Hz")
    becquerel = si.register_unit(1 / second, "Becquerel", "Bq")
    sievert = si.register_unit(joule / kilogram, "Sievert", "Sv")
    gray = si.register_unit(joule / kilogram, "Gray", "Gy")
    pascal = si.register_unit(newton / metre**2, "Pascal", "Pa")
    siemens = si.register_unit(1 / ohm, "Siemens", "S")
    steradian = si.register_unit(radian**2, "Steradian", "sr")
    lumen = si.register_unit(candela * steradian, "Lumen", "lm")
    lux = si.register_unit(lumen / metre**2, "Lux", "lx")
    katal = si.register_unit(mole / second, "Katal", "kat")

    # Non-si units
    minute = si.register_unit(sc.minute * second, "Minute", "min")
    hour = si.register_unit(sc.hour * second, "Hour", "hr")
    # day = si.register_unit(sc.day * second, "Day", "d")  # conflict!
    # year = si.register_unit(sc.year * second, "Year", "a")  # conflict!
    julian_year = si.register_unit(sc.Julian_year * second, "Julian year", "yr")
    # inch = si.register_unit(sc.inch * metre, "Inch", "in")  # conflict!
    foot = si.register_unit(sc.foot * metre, "Foot", "ft")
    yard = si.register_unit(sc.yard * metre, "Yard", "yd")
    mile = si.register_unit(sc.mile * metre, "Mile", "mi")
    mil = si.register_unit(sc.mil * metre, "Mil", "mil")
    angstrom = si.register_unit(sc.angstrom * metre, u"Ångström", u"Å", "\\AA")
    astronomical_unit = si.register_unit(sc.au * metre,
                                         "Astronomical unit", "au")
    light_year = si.register_unit(sc.light_year * metre, "Light year", "ly")
    # parsec = si.register_unit(sc.parsec * metre, "Parsec", "pc")  # conflict!
    atmosphere = si.register_unit(sc.atm * pascal, "Atmosphere", "atm")
    bar = si.register_unit(sc.bar * pascal, "Bar", "bar")

    litre = si.register_unit(sc.litre * metre**3, "Litre", "l")
    erg = si.register_unit(sc.erg * joule, "Erg", "erg")
    arc_minute = si.register_unit(sc.arcmin * radian, "Arc minute", "'")
    arc_second = si.register_unit(sc.arcsec * radian, "Arc second", "''")
    degree = si.register_unit(sc.degree * radian, "Degree", "°", "{}^{\\circ}")
    dalton = si.register_unit(sc.u * kilogram, "Dalton", "Da")
    # conflict!
    # unit = si.register_unit(sc.u * kilogram, "Atomic mass unit", "u")
    are = si.register_unit((10 * metre)**2, "Are", "ar")
    hectare = si.register_unit((100 * metre)**2, "Hectare", "ha")
    gauss = si.register_unit(0.0001 * tesla, "Gauss", "G")
    barn = si.register_unit(1e-28 * metre**2, "Barn", "b")

    electron_volt = si.register_unit(sc.e * joule, "Electronvolt", "eV")
    speed_of_light = si.register_unit(sc.c * metre / second,
                                      "Speed of light", "c")
    planck_constant = si.register_unit(sc.h * joule * second,
                                       "Planck constant", "h")
    hbar = si.register_unit(sc.hbar * joule * second,
                             "Reduced Planck constant", "h_bar", "\\hbar")

    units = {
        "ampere": ampere,
        "angstrom": angstrom,
        "arc_minute": arc_minute,
        "arc_second": arc_second,
        "are": are,
        "astronomical_unit": astronomical_unit,
        "atmosphere": atmosphere,
        "bar": bar,
        "barn": barn,
        "becquerel": becquerel,
        "c": speed_of_light,
        "candela": candela,
        "coulomb": coulomb,
        "dalton": dalton,
        "degree": degree,
        "electron_volt": electron_volt,
        "erg": erg,
        "farad": farad,
        "foot": foot,
        "gauss": gauss,
        "gram": gram,
        "gray": gray,
        "h": planck_constant,
        "hbar": hbar,
        "hectare": hectare,
        "henry": henry,
        "hertz": hertz,
        "hour": hour,
        #"inch": inch,
        "joule": joule,
        "julian_year": julian_year,
        "kat": katal,
        "kelvin": kelvin,
        "kilogram": kilogram,
        "light_year": light_year,
        "litre": litre,
        "liter": litre,
        "lumen": lumen,
        "lux": lux,
        "meter": metre,
        "metre": metre,
        "mil": mil,
        "mile": mile,
        "minute": minute,
        "mole": mole,
        "newton": newton,
        "ohm": ohm,
        #"parsec": parsec,
        "pascal": pascal,
        "planck_constant": planck_constant,
        "radian": radian,
        "second": second,
        "siemens": siemens,
        "sievert": sievert,
        "speed_of_light": speed_of_light,
        "steradian": steradian,
        "tesla": tesla,
        "volt": volt,
        "watt": watt,
        "weber": weber,
        "yard": yard,
        #"year": year,
    }

    prefixes = {
        "yocto": yocto,
        "zepto": zepto,
        "atto": atto,
        "femto": femto, 
        "pico": pico,
        "nano": nano,
        "micro": micro,
        "milli": milli,
        "centi": centi,
        "deci": deci,
        "deca": deca,
        "hecto": hecto,
        "kilo": kilo,
        "mega": mega,
        "giga": giga,
        "tera": tera,
        "peta": peta,
        "exa": exa,
        "zetta": zetta,
        "yotta": yotta,
    }

    return si, prefixes, units

unit_system, prefixes, units = create_systeme_international()

globals().update(units)
globals().update(prefixes)

del units
del prefixes
