# -------------------------------------------------------------------------------------------------
# Quantum Feature Detector
# Copyright 2018 QxBranch, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# To learn more about QxBranch, see <https://www.qxbranch.com>.
# -------------------------------------------------------------------------------------------------

from os import path
from setuptools import setup


__name__ = 'qxbranch.quantum_feature_detector'
__author__ = 'QxBranch, Inc.'
__email__ = 'support@qxbranch.com'

# Get the version number from the VERSION file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'VERSION.txt')) as f:
    __version__ = f.read()

with open(path.join(here, 'README.rst'), 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(name=__name__,
      description="A Python application by QxBranch for running Quantum Feature Detectors",
      url='http://www.qxbranch.com',
      long_description=long_description,
      author=__author__,
      author_email=__email__,
      license='Copyright 2018 QxBranch, Inc.',
      keywords=['qxbranch', 'quantum', 'machine learning'],
      packages=['qxbranch.quantum_feature_detector',
                'qxbranch.quantum_feature_detector.pyquil'],
      install_requires=['numpy==1.15.4', 'pyquil>=2.0.0', 'matplotlib==3.0.2', 'scikit-learn==0.20.0', 'networkx==2.2'],
      version=__version__,
      tests_require=['pytest'],
      data_files=[('', ['LICENSE-2.0.txt', 'README.rst'])],
      )
