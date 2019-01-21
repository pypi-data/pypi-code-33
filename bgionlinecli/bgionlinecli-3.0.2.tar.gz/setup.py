# Copyright (C) 2016-2017,BGI ltd.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from setuptools import setup, find_packages
import re,sys
if sys.version_info < (2, 7) and sys.version_info > (2, 7):
    raise Exception(""
                    "bo requires Python >= 2.7")
with open('bgionline/version.py', 'r') as fd:
    client_version = re.search(r'^client_version\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)


setup(
    name='bgionlinecli',
    version=client_version,
    description='BGI Online Platform API bindings for Python',
    author='bgionline',
    author_email='bgionline@genomics.cn',
    url='https://www.bgionline.cn',
    zip_safe=False,
    license='Apache Software License',
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    entry_points={
        "console_scripts": ["bo=bgionline.scripts.bo:main", ],
    },
    test_suite="",
    tests_require=['oss2==2.3.4', 'boto3==1.4.6', 'chardet==3.0.4', 'requests==2.18.4', 'psutil==5.4.1', 'blessings==1.6','pyreadline==2.1'],
    install_requires=['oss2==2.3.4', 'boto3==1.4.6', 'chardet==3.0.4', 'requests==2.18.4', 'psutil==5.4.1', 'blessings==1.6','pyreadline==2.1'],
)
