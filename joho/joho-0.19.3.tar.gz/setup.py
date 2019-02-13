#!python
# -*- coding: utf-8 -*-
from setuptools import setup
setup(
   name='joho',
   version='0.19.3',
   description='HTML and SVG module to create lecture materials for 情報処理及び実習 TAC101  at University of Yamanashi (山梨大学).',
   author='CHEN, Lee Chuin',
   author_email='leechuin@yamanashi.ac.jp',
   license='MIT',
   python_requires='>=2',
   long_description=open('README.rst').read(),
   classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Text Processing :: Markup :: HTML',
        'License :: OSI Approved :: MIT License',
    ],
   keywords='html svg joho',
   packages=['joho'],  #same as name
   install_requires=['numpy', 'matplotlib'], #external packages as dependencies
)
