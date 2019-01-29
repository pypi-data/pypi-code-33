#!/usr/bin/env python
# Copyright (c) 2017 Radware LTD. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO - DO NOT EDIT
from distutils import log
import os
from setuptools import setup
from setuptools.command.install import install

DEFAULT_CONFIG = '\
[DEFAULT]\n\
vdirect_address = \n\
#ha_secondary_address = \n\
#vdirect_user = vDirect\n\
#vdirect_password = \n\
#port = 2189\n\
#ssl = true\n\
#ssl_verify_context = true\n\
#timeout = 5000\n\
#base_uri = \n\
#service_adc_type = VA\n\
#service_ha_pair = false\n\
#configure_allowed_address_pairs = false\n\
#service_throughput = 1000\n\
#service_ssl_throughput = 100\n\
#service_compression_throughput = 100\n\
#service_cache = 20\n\
#service_resource_pool_ids = \n\
#service_isl_vlan = -1\n\
#service_session_mirroring_enabled = false'


class OverrideInstall(install):

    def run(self):
        file_mode = 0o644
        folder_mode = 0o755
        install.run(self)

        log.info("Changing the package folder permissions to %s" % (oct(folder_mode)))
        dirname = os.path.dirname(self.get_outputs()[0])
        os.chmod(dirname, folder_mode)

        log.info("Changing files permissions to %s" % (oct(file_mode)))
        for filepath in self.get_outputs():
            os.chmod(filepath, file_mode)

        log.info("Creating /etc/radware/ folder")
        if not os.path.exists('/etc/radware/'):
            os.mkdir('/etc/radware/', folder_mode)
            log.info("Changing permissions for  /etc/radware/ folder")
            os.chmod('/etc/radware', folder_mode)
        if not os.path.exists('/etc/radware/radware_lbaas_driver.conf'):
            log.info("Writing default configuration file")
            cf = os.open('/etc/radware/radware_lbaas_driver.conf', os.O_CREAT | os.O_RDWR, 0o755)
            os.write(cf, DEFAULT_CONFIG)
            os.chmod('/etc/radware/radware_lbaas_driver.conf', file_mode)
            os.close(cf)
        else:
            log.info("Preserving existing configuration file")


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='radware_nlbaas_v2_mitaka_driver',
      version='4.7.0-2',
      description='Neutron LBaaS Radware driver for Openstack Mitaka',
      long_description = readme(),
      classifiers=[
        'Environment :: OpenStack',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7'
      ],
      keywords=['radware', 'vdirect', 'lbaas', 'ADC', 'neutron LBaaS v2'],
      url='https://pypi.python.org/pypi/radware_nlbaas_v2_mitaka_driver',
      author='Evgeny Fedoruk, Radware',
      author_email='evgenyf@radware.com',
      packages=['radware_nlbaas_v2_mitaka_driver'],
      zip_safe=False,
      cmdclass={'install': OverrideInstall})
