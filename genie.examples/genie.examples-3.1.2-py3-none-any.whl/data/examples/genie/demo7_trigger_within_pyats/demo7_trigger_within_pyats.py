#!/bin/env python
###################################################################
# basic_example.py : A very simple test script example which include:
#     common_setup
#     Tescases
#     common_cleanup
# The purpose of this sample test script is to show the "hello world"
# of aetest.
###################################################################

# To get a logger for the script
import logging

# Needed for aetest script
from ats import aetest

# Genie Imports
# Pre-processor to set Genie harness information.
from genie.harness.standalone import genie_parameters
from genie.conf import Genie

# Verifications classes and template class which is used for verifications
# using parser or Genie Ops.

from genie.harness.base import TestcaseVerificationOps, Template

# Trigger to execute
from genie.libs.sdk.triggers.sleep.sleep import TriggerSleep
from genie.libs.sdk.triggers.shutnoshut.bgp.shutnoshut import TriggerShutNoShutBgp

# Get your logger for your script
log = logging.getLogger(__name__)


###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

# This is how to create a CommonSetup
# You can have one of no CommonSetup
# CommonSetup can be named whatever you want

class common_setup(aetest.CommonSetup):
    """ Common Setup section """

    # CommonSetup have subsection.
    # You can have 1 to as many subsection as wanted
    # here is an example of 2 subsections

    # First subsection
    @aetest.subsection
    def sample_subsection_1(self):
        """ Common Setup subsection """
        log.info("Aetest Common Setup ")

    @aetest.subsection
    def connect(self, testbed):
        genie_testbed = Genie.init(testbed)
        self.parent.parameters['testbed'] = genie_testbed
        uut = genie_testbed.devices['uut']
        uut.connect()

    # If you want to get the name of current section,
    # add section to the argument of the function.

    # Second subsection
    @aetest.subsection
    def sample_subsection_2(self, section):
        """ Common Setup subsection """
        log.info("Inside %s" % (section))

        # And how to access the class itself ?

        # self refers to the instance of that class, and remains consistent
        # throughout the execution of that container.
        log.info("Inside class %s" % (self.uid))

###################################################################
###                     TESTCASES SECTION                       ###
###################################################################

# This is how to create a testcase
# You can have 0 to as many testcases as wanted

# Testcase name : tc_one
class tc_one(aetest.Testcase):
    """ This is user Testcases section """

    # Testcases are divided into 3 sections
    # Setup, Test and Cleanup.

    # This is how to create a setup section
    @aetest.setup
    def prepare_testcase(self, section):
        """ Testcase Setup section """
        log.info("Preparing the test")
        log.info(section)

    # This is how to create a test section
    # You can have 0 to as many test section as wanted

    # First test section
    @ aetest.test
    def simple_test_1(self, speed=50):
        """ Sample test section. Only print """
        log.info("First test section ")

    # Second test section
    @ aetest.test
    def simple_test_2(self):
        """ Sample test section. Only print """
        log.info("Second test section ")

    # This is how to create a cleanup section
    @aetest.cleanup
    def clean_testcase(self):
        """ Testcase cleanup section """
        log.info("Pass testcase cleanup")

#####################################################################
####                 Genie Harness information                    ###
#####################################################################

# Run verification
# Enter the name of the verification name which
# matches the one in the datafile.
@aetest.processors(pre=[genie_parameters])
class Verify_BgpVrfAllAll_1(TestcaseVerificationOps):
    # Change _ for the . format.
    uid = 'Verify_BgpVrfAllAll.1'
    child = Template


# Execute a trigger.
@aetest.processors(pre=[genie_parameters])
class TriggerSleep(TriggerSleep):
    pass


# Run verification
# Enter the name of the verification name which
# matches the one in the datafile.
@aetest.processors(pre=[genie_parameters])
class Verify_BgpVrfAllAll_2(TestcaseVerificationOps):
    # Change _ for the . format.
    uid = 'Verify_BgpVrfAllAll.2'
    child = Template

# Execute a trigger.
@aetest.processors(pre=[genie_parameters])
class TriggerShutNoShutBgp(TriggerShutNoShutBgp):
    pass

# Run verification
# Enter the name of the verification name which
# matches the one in the datafile.
@aetest.processors(pre=[genie_parameters])
class Verify_BgpVrfAllAll_3(TestcaseVerificationOps):
    # Change _ for the . format.
    uid = 'Verify_BgpVrfAllAll.3'
    child = Template

#####################################################################
####                       COMMON CLEANUP SECTION                 ###
#####################################################################

# This is how to create a CommonCleanup
# You can have 0 , or 1 CommonCleanup.
# CommonCleanup can be named whatever you want :)
class common_cleanup(aetest.CommonCleanup):
    """ Common Cleanup for Sample Test """

    # CommonCleanup follow exactly the same rule as CommonSetup regarding
    # subsection
    # You can have 1 to as many subsections as wanted
    # here is an example of 1 subsection

    @aetest.subsection
    def clean_everything(self):
        """ Common Cleanup Subsection """
        log.info("Aetest Common Cleanup ")

if __name__ == '__main__': # pragma: no cover
    aetest.main()
