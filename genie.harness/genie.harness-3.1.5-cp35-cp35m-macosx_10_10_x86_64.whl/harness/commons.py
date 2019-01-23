# ATS
from ats import aetest

from . import _commons_internal

# subsections for common_setup
@aetest.subsection
def connect(self, testbed, steps):
    '''Connect all the devices defined in mapping file'''
    return _commons_internal.connect(self, testbed, steps)

@aetest.subsection
def disconnect(self, testbed, steps):
    '''Connect all the devices defined in mapping file'''
    return _commons_internal.disconnect(self, testbed, steps)

@aetest.subsection
def configure(self, testbed, steps):
    '''Configure the devices'''
    return _commons_internal.configure(self, testbed, steps)

@aetest.subsection
def check_config(self, testbed, testscript, steps, devices=None):
    '''Take snapshot of configuration for each devices'''
    return _commons_internal.check_config(self, testbed, testscript, steps,
                                          devices)

@aetest.subsection
def initialize_traffic(self, steps, testbed):

    return _commons_internal.initialize_traffic(self, steps, testbed)

# subsections for common_cleanup
@aetest.subsection
def check_post_config(self, testbed, testscript, steps, configs=None):
    '''Verify the configuration for the devices has not changed'''
    return _commons_internal.check_post_config(self, testbed, testscript,
                                               steps, configs)

# subsections for common_cleanup
@aetest.subsection
def stop_traffic(self, testbed, steps):
    return _commons_internal.stop_traffic(self, testbed, steps)


class ProfileSystem(object):

    @aetest.subsection
    def ProfileSystem(self, feature, container, testscript, testbed, steps):
        return _commons_internal.ProfileSystem.ProfileSystem(self, feature,
                                                            container,
                                                            testscript, testbed,
                                                            steps)
