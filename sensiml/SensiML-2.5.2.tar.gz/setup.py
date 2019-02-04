################################################################################                                                       #
#                                                                              #
#  Copyright (c) 2017-18  SENSIML Corporation.                                 #
#                                                                              #
#  The source code contained or  described  herein and all documents related   #
#  to the  source  code ("Material")  are  owned by SENSIML Corporation or its #
#  suppliers or licensors. Title to the Material remains with SENSIML Corpora- #
#  tion  or  its  suppliers  and  licensors. The Material may contain trade    #
#  secrets and proprietary and confidential information of SENSIML Corporation #
#  and its suppliers and licensors, and is protected by worldwide copyright    #
#  and trade secret laws and treaty provisions. No part of the Material may    #
#  be used,  copied,  reproduced,  modified,  published,  uploaded,  posted,   #
#  transmitted, distributed,  or disclosed in any way without SENSIML's prior  #
#  express written permission.                                                 #
#                                                                              #
#  No license under any patent, copyright,trade secret or other intellectual   #
#  property  right  is  granted  to  or  conferred upon you by disclosure or   #
#  delivery of the Materials, either expressly, by implication,  inducement,   #
#  estoppel or otherwise.Any license under such intellectual property rights   #
#  must be express and approved by SENSIML in writing.                         #
#                                                                              #
#  Unless otherwise agreed by SENSIML in writing, you may not remove or alter  #
#  this notice or any other notice embedded in Materials by SENSIML or         #
#  SENSIML's suppliers or licensors in any way.                                #
#                                                                              #
################################################################################

import sys
import os
from setuptools import setup, find_packages

__version__ = "2.5.2"

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

setup(
    name='SensiML',
    description='SensiML Analytic Suite Python client',
    version=__version__,
    author='SensiML',
    author_email='support@sensiml.com',
    license='Proprietary',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['*test*', ]),
    package_data={
        'sensiml.datasets': ['*.csv'],
        'sensiml.widgets': ['*.pem'],
        'sensiml.image': ['*.png'],
    },
    include_package_data=True,
    long_description=open('README.md').read(),
    install_requires=[
        'cookiejar',
        'requests>=2.14.2',
        'requests-oauthlib>=0.7.0',
        'appdirs>=1.4.3',
        'semantic_version>=2.6.0',
        'jupyter>=1.0.0',
        'numpy>=1.13',
        'pandas>=0.20.3',
        'matplotlib>=2.0.0',
        'nrfutil>=3.3.2',
        'qgrid>=1.0.2',
        'prompt-toolkit>=2.0.5; python_version>="3"',
        'prompt-toolkit<=1.0.4; python_version<"3"',
        'jupyter-console>=6.0.0; python_version>="3"',
        'jupyter-console<=5.2.0; python_version<"3"',
        'ipython>=7.0.1; python_version>="3"',
        'ipython<=5.8.0; python_version<"3"',
        'bqplot',
        'seaborn',
        'wurlitzer',
        'jupyter-contrib-nbextensions',
        'pyserial',
    ],
)
