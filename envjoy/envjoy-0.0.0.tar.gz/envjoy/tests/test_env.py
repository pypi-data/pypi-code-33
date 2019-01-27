
# =========================================
#       IMPORTS
# --------------------------------------

from os import environ as env

import rootpath

rootpath.append()

from envjoy.tests import helper

import envjoy

env['COLORS'] = 'true' # lower prio
env['VERBOSE'] = 'true' # lower prio

env['ENV_COLORS'] = 'false' # higher prio
env['ENV_VERBOSE'] = 'false' # higher prio


# =========================================
#       TEST
# --------------------------------------

class TestCase(helper.TestCase):

    # NOTE: quite basic test right now, should add more advanced error message formatting assertions

    def test__import(self):
        self.assertModule(envjoy)


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':
    helper.run(TestCase)
