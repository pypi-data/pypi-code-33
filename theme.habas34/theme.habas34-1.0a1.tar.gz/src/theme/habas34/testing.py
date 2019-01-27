# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import theme.habas34


class ThemeHabas34Layer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=theme.habas34)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'theme.habas34:default')


THEME_HABAS34_FIXTURE = ThemeHabas34Layer()


THEME_HABAS34_INTEGRATION_TESTING = IntegrationTesting(
    bases=(THEME_HABAS34_FIXTURE,),
    name='ThemeHabas34Layer:IntegrationTesting',
)


THEME_HABAS34_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(THEME_HABAS34_FIXTURE,),
    name='ThemeHabas34Layer:FunctionalTesting',
)


THEME_HABAS34_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        THEME_HABAS34_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='ThemeHabas34Layer:AcceptanceTesting',
)
