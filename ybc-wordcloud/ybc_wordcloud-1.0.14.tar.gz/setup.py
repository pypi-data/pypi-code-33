#!/usr/bin/env python

from distutils.core import setup

setup(name='ybc_wordcloud',
      version='1.0.14',
      description='Generate wordcloud.',
      long_description='Generate text wordcloud according word frequency.',
      author='zhangyun',
      author_email='zhangyun@fenbi.com',
      keywords=['python', 'wordcloud', 'text wordcloud'],
      url='http://pip.zhenguanyu.com/',
      packages=['ybc_wordcloud'],
      package_data={'ybc_wordcloud': ['test.jpg', 'text.txt', '*.py']},
      license='MIT',
      install_requires=['ybc_config', 'requests', 'Pillow', 'ybc_exception']
      )