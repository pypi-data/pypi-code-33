#!/usr/bin/env python
# -- coding: utf-8 --
# Copyright 2017 Reactive Ops Inc.
#
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    print("setup tools required. Please run: "
          "pip install setuptools).")
    sys.exit(1)

setup(name='pentagon_datadog',
      version='1.10.1',
      description='Pentagon Component to install common datadog monitors',
      author='ReactiveOp Inc.',
      author_email='reactive@reactiveops.com',
      url='http://reactiveops.com/',
      license='Apache2.0',
      include_package_data=True,
      install_requires=[
          'oyaml>=0.4',
          'pentagon>=2.4.1'
          ],
      data_files=[],
      package_data={
        "pentagon_datadog": [
          'files/*',
          'files/datadog/*',
          'monitors/aws/*',
          'monitors/gcp/*',
          'monitors/gcp-quotas/*',
          'monitors/kubernetes/*',
          'monitors/elasticsearch/*',
          'monitors/rds/*',
          'dashboards/kubernetes/*'
        ]
      },
      packages=find_packages(exclude=('test'))
      )
