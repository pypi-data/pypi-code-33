
__all__ = [
    'go_provinces',
    'go_cities',
    'go_districts',
    'go_getName',
    'go_parseAddress',
    'go_provinceCodes',
    'go_cityCodes',
    'go_districtCodes',
    'go_getProvinceCode',
    'go_getCityCode',
    'go_getDistrictCode',
    'go_getCode',
    'go_parseCode',
]

from ctypes import CDLL
import ctypes
from pathlib import Path


# +++++ 初始化 ++++++
# 加载dll
dir = Path(__file__).parent
dll_path = str(dir / 'addlib.so')
cdll = CDLL(dll_path)
# 读地址数据
go_initialize = cdll.initialize
go_initialize.argtypes = [ctypes.c_char_p]
go_initialize.restype = ctypes.c_char_p
data_path = str(dir / 'lib.add')
go_initialize(data_path.encode('utf-8'))
# +++++++++++++++++++

go_provinces = cdll.provinces
go_provinces.restype = ctypes.c_char_p

go_cities = cdll.cities
go_cities.argtypes = [ctypes.c_char_p]
go_cities.restype = ctypes.c_char_p

go_districts = cdll.districts
go_districts.argtypes = [ctypes.c_char_p]
go_districts.restype = ctypes.c_char_p

go_getName = cdll.getName
go_getName.argtypes = [ctypes.c_char_p]
go_getName.restype = ctypes.c_char_p

go_parseAddress = cdll.parseAddress
go_parseAddress.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
go_parseAddress.restype = ctypes.c_char_p

go_provinceCodes = cdll.provinceCodes
go_provinceCodes.restype = ctypes.c_char_p

go_cityCodes = cdll.cityCodes
go_cityCodes.argtypes = [ctypes.c_char_p]
go_cityCodes.restype = ctypes.c_char_p

go_districtCodes = cdll.districtCodes
go_districts.argtypes = [ctypes.c_char_p]
go_districtCodes.restype = ctypes.c_char_p

go_getCode = cdll.getCode
go_getCode.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
go_getCode.restype = ctypes.c_char_p

go_getProvinceCode = cdll.getProvinceCode
go_getProvinceCode.argtypes = [ctypes.c_char_p]
go_getProvinceCode.restype = ctypes.c_char_p

go_getCityCode = cdll.getCityCode
go_getCityCode.argtypes = [ctypes.c_char_p]
go_getCityCode.restype = ctypes.c_char_p

go_getDistrictCode = cdll.getDistrictCode
go_getDistrictCode.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
go_getDistrictCode.restype = ctypes.c_char_p

go_parseCode = cdll.parseCode
go_parseCode.argtypes = [ctypes.c_char_p]
go_parseCode.restype = ctypes.c_char_p