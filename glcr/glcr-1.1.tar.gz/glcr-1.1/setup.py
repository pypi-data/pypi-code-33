import setuptools
from distutils.core import setup
import sys
from distutils.core import setup, Extension
from sysconfig import get_paths

import numpy

if sys.version_info.major < 3:
    sys.exit('Sorry, Python < 3 is not supported')

sfc_module = Extension(
    'glcr',
    sources=[
        'esa/GSA.cpp', 'esa/lcp.cpp', 'esa/skew.cpp', 'glcr.cpp',
        'lcx/GLCR.cpp', 'lcx/LCR.cpp', 'lcx/LCS.cpp', 'lcx/LCX.cpp',
        'lcx/lv/GLCR_last_visited_int.cpp', 'lcx/lv/LCR_last_visited.cpp',
        'lcx/lv/LCR_last_visited_int.cpp', 'lcx/lv/LCS_last_visited.cpp',
        'lcx/lv/LCS_last_visited_int.cpp', 'lcx/lv/util/LV_list_glcr_int.cpp',
        'lcx/lv/util/LV_list_item.cpp', 'lcx/lv/util/LV_list_lcr.cpp',
        'lcx/lv/util/LV_list_lcr_int.cpp', 'lcx/lv/util/LV_list_lcs.cpp',
        'lcx/lv/util/LV_list_lcs_int.cpp', 'lcx/lv/util/Priority_QLS.cpp',
        'lcx/lv/util/QLS_item.cpp', 'lcx/Result.cpp', 'lcx/Result_saver.cpp',
        'TC_reader.cpp'],
    include_dirs=[get_paths()['include'], numpy.get_include()],
    language='c++')

setup(name='glcr', version='1.1',
      description='Python Package with glcr C++ extension',
      ext_modules=[sfc_module]
      )
