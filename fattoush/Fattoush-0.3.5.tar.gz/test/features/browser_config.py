# -*- coding: utf-8 -*-
import json

import mock

from fattoush import step
from fattoush.config import FattoushConfig
from lettuce import world
from nose.tools import assert_equals


@step(u'Given I pass desired capabilites of "(.*)"')
def given_i_pass_desired_capabilites_of_group1(step, capabilities_json):
    world.per_scenario['capabilities'] = json.loads(capabilities_json)


@step(u'When fattoush creates a configurations from this')
def when_fattoush_creates_a_configurations_from_this(step):
    capabilities = world.per_scenario['capabilities']

    world.per_scenario['config'] = FattoushConfig(
        index=None,
        browser=capabilities,
        server={},
        lettuce=mock.MagicMock(),
    )


@step(u'Then the configuration name is "([^"]*)"')
def then_the_configuration_name_is_group1(step, name):
    assert_equals(world.per_scenario['config'].name, name)


@step(u'Then it does not crash')
def then_it_does_not_crash(_):
    # This is a no-op, as it is essentially just saying that
    # the previous step did not raise an exception - if that
    # were not true we would never reach this step.
    pass
