# -*- coding: utf-8 -*-

from distutils.core import setup


LICENSE = 'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)'


setup(
    name='explainer',
    version='0.0.2dev',
    description=('The first unified explainability toolkit for '
                 'explainable software and hardware systems.'),
    author='Maximilian Köhl',
    author_email='mail@koehlma.de',
    url='https://github.com/explainable-systems/explainer',
    license='LGPLv3',
    modules=['explainer'],
    requires=['shap', 'eliot'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        LICENSE,
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Debuggers',
        'Topic :: System :: Monitoring'
    ]
)

