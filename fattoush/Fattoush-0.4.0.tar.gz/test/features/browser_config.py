# -*- coding: utf-8 -*-
import json

import mock

import fattoush

from fattoush.config import FattoushConfig

from fattoush.decorators import step


@step.without_step(u'Given I pass desired capabilities of "(.*)"')
def given_i_pass_desired_capabilities_of(capabilities_json):
    fattoush.per.scenario['capabilities'] = json.loads(capabilities_json)


@step.without_step(u'When fattoush creates a configurations from this')
def when_fattoush_creates_a_configurations_from_this():
    fattoush.per.scenario['config'] = FattoushConfig(
        index=None,
        browser={
            'capabilities': fattoush.per.scenario['capabilities'],
            'options': fattoush.per.scenario.get('options', {})
        },
        server={},
        lettuce_cfg=mock.MagicMock(),
    )


@step.without_step(u'the configuration name is "([^"]*)"')
def then_the_configuration_name_is(expected):
    config = fattoush.per.scenario['config']
    actual = config.name

    assert actual == expected, 'Expected {!r} but got {!r}'.format(
        expected, actual
    )


@step.just_hashes(u'the configuration has options:')
def the_configuration_name_is(dicts):
    config = fattoush.per.scenario['config']
    options = config.options()

    expected = [dict_['option'] for dict_ in dicts]
    actual = options.arguments

    assert actual == expected, 'Expected {!r} but got {!r}'.format(
        expected, actual
    )


@step.without_step(u'Then it does not crash')
def then_it_does_not_crash():
    # This is a no-op, as it is essentially just saying that
    # the previous step did not raise an exception - if that
    # were not true we would never reach this step.
    pass


@step.just_hashes(u'And I pass browser options:')
def and_i_pass_browser_options(dicts):
    fattoush.per.scenario['options'] = [dict_['option'] for dict_ in dicts]
