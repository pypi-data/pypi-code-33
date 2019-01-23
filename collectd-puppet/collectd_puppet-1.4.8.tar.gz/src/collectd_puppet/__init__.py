# Copyright 2018 CERN
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
collectd sensor for puppet's last_run_summary.yaml file.

To configure with collectd

<Plugin "python">
  LogTraces true
  Interactive false
  Import "collectd_puppet"
  <Module "collectd_puppet">
    path "/opt/puppetlabs/puppet/cache/state/last_run_summary.yaml"
  </Module>
</Plugin>
"""

import os
import time
import collectd
import yaml

PATH = "/opt/puppetlabs/puppet/cache/state/last_run_summary.yaml"
STATE = "/var/lib/collectd/puppet.state"
MAX_RETENTION = 60*60*6

META = {'schema_version': 1}

def config_func(config):
    """ accept configuration from collectd """
    path_set = False
    for node in config.children:
        key = node.key.lower()
        val = node.values[0]
        if key == 'path':
            global PATH
            PATH = val
            path_set = True
        else:
            collectd.info('puppet plugin: Unknown config key "%s"' % key)

    if path_set:
        collectd.info('puppet plugin: Using overridden path %s' % PATH)
    else:
        collectd.info('puppet plugin: Using default path %s' % PATH)

def read_func():
    """ open yaml file and publish if Puppet has run """
    try:
        last_polled = os.stat(STATE).st_mtime
    except OSError:
        last_polled = 0
    last_puppet_run = os.stat(PATH).st_mtime

    if last_polled >= last_puppet_run:
        return

    with open(PATH, 'r') as stream:
        try:
            data = yaml.load(stream)
            with open(STATE, 'a'):
                os.utime(STATE, None)
        except yaml.YAMLError as exc:
            print exc

    # puppet_time type.
    # This type is always populated, even on a compilation error
    times = [
        data['time']['last_run'],
        1 if 'resources' in data else 0,
    ]
    val = collectd.Values(plugin='puppet',)
    val.type = 'puppet_time'
    val.meta = META
    val.values = times
    val.dispatch(interval=MAX_RETENTION)

    # puppet_run type
    # this type is not populated in certain cases, e.g compilation
    # error.
    if 'resources' in data:
        run = [
            data['resources']['total'],
            data['resources']['changed'],
            data['resources']['corrective_change'],
            data['resources']['failed'],
            data['resources']['failed_to_restart'],
            data['resources']['out_of_sync'],
            data['resources']['restarted'],
            data['resources']['scheduled'],
            data['resources']['skipped'],
            data['time']['total'],
            data['time']['config_retrieval'],
        ]
        val = collectd.Values(plugin='puppet',)
        val.type = 'puppet_run'
        val.meta = META
        val.values = run
        val.dispatch(interval=MAX_RETENTION)

collectd.register_config(config_func)
collectd.register_read(read_func)
