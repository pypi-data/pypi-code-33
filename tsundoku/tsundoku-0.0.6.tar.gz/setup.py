# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-17 alvations
# URL:
# For license information, see LICENSE.md

from distutils.core import setup

setup(
    name='tsundoku',
    version='0.0.6',
    packages=['tsundoku',],
    url = 'https://github.com/alvations/tsundonku',
    description='Coursework for Text Processing using Machine Learning at NUS-ISS',
    license="MIT",
	install_requires = ['IPython', 'torch', 'nltk', 'gensim', 'tqdm', 'numpy'],
)
