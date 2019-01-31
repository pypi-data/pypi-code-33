#!/usr/bin/env python

from distutils.core import setup

setup(name='ybc_idcard_ocr',
      version='1.0.8',
      description='Recognize ID Card By Ocr.',
      long_description='Recognize ID Card By Ocr.',
      author='hurs',
      author_email='hurs@fenbi.com',
      keywords=['python', 'idcard', 'ocr'],
      url='http://pip.zhenguanyu.com/',
      packages=['ybc_idcard_ocr'],
      package_data={'ybc_idcard_ocr': ['test.jpg', '*.py']},
      license='MIT',
      install_requires=['requests', 'ybc_config', 'opencv-python', 'pillow', 'ybc_exception']
      )