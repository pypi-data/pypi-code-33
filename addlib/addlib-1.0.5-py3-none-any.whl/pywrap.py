
__all__ = [
    'provinces',
    'cities',
    'districts',
    'get_name',
    'parse_address',
    'province_codes',
    'city_codes',
    'district_codes',
    'get_code',
    'get_province_code',
    'get_city_code',
    'get_district_code',
    'parse_code'
]

from .gomethods import *


def provinces():
    return go_provinces().decode('utf-8').split('\t')


def cities(of_province):
    p = of_province.encode('utf-8')
    return go_cities(p).decode('utf-8').split('\t')


def districts(of_city):
    c = of_city.encode('utf-8')
    return go_districts(c).decode('utf-8').split('\t')


def get_name(code):
    c = code.encode('utf-8')
    return go_getName(c).decode('utf-8')


def parse_address(province_name=None, city_name=None, district_name=None):
    p = province_name.encode('utf-8') if province_name else b''
    c = city_name.encode('utf-8') if city_name else b''
    d = district_name.encode('utf-8') if district_name else b''
    return go_parseAddress(p, c, d).decode('utf-8').split('\t')


def province_codes():
    return go_provinceCodes().decode('utf-8').split('\t')


def city_codes(of_province):
    p = of_province.encode('utf-8')
    return go_cityCodes(p).decode('utf-8').split('\t')


def district_codes(of_city):
    c = of_city.encode('utf-8')
    return go_districtCodes(c).decode('utf-8').split('\t')


def get_code(province_name=None, city_name=None, district_name=None):
    p = province_name.encode('utf-8') if province_name else b''
    c = city_name.encode('utf-8') if city_name else b''
    d = district_name.encode('utf-8') if district_name else b''
    return go_getCode(p, c, d).decode('utf-8')


def get_province_code(province_name):
    p = province_name.encode('utf-8')
    return go_getProvinceCode(p).decode('utf-8')


def get_city_code(city_name):
    c = city_name.encode('utf-8')
    return go_getCityCode(c).decode('utf-8')


def get_district_code(city_name, district_name):
    c = city_name.encode('utf-8')
    d = district_name.encode('utf-8')
    return go_getDistrictCode(c, d).decode('utf-8')


def parse_code(code):
    c = code.encode('utf-8')
    return go_parseCode(c).decode('utf-8').split('\t')
