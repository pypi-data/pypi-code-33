# (c) 2014 Mind Candy Ltd. All Rights Reserved.
# Licensed under the MIT License; you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

"""
The driver class shall be a subclass of WebDriver with a classmethod
`instance()` which takes the current step or feature and returns
the active WebDriver instance.
"""

from selenium.webdriver import Remote
from lettuce.core import Step, Scenario
from lettuce import world
from .sauce import Sauce, Local


class Driver(Remote):

    @classmethod
    def _scenario(cls, step_or_scenario):
        if isinstance(step_or_scenario, Scenario):
            return step_or_scenario.name

        if isinstance(step_or_scenario, Step):
            step = step_or_scenario

            if getattr(step, 'scenario', None) is not None:
                return step.scenario.name

            if getattr(step, 'background', None) is not None:
                return repr(step)

        raise TypeError("{0} is not an instance of {1} or {2}"
                        .format(step_or_scenario, Step, Scenario))

    @classmethod
    def instance(cls, step_or_scenario):
        """
        :rtype : Driver
        """

        if 'browser' not in world.per_scenario:
            world.per_scenario['browser'] = cls(
                world.fattoush,
                cls._scenario(step_or_scenario),
            )

        return world.per_scenario['browser']

    @classmethod
    def got_instance(cls):
        return 'browser' in world.per_scenario

    @classmethod
    def kill_instance(cls):
        browser = world.per_scenario.pop('browser', None)

        if browser is not None:
            browser.quit()

    def __init__(self, config, name):
        """
        :param config: fattoush.config.FattoushConfig
        :param scenario: Scenario
        """
        self.fattoush_config = config

        super(Driver, self).__init__(
            config.command_executor,
            config.desired_capabilities(name),
        )

        # For saucelabs you need a user name and an auth key
        self.is_sauce = "user" in config.server

        cls = Sauce if self.is_sauce else Local
        self.sauce = cls(config=config, browser=self)
